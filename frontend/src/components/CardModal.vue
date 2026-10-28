<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '../api/client'
import type { Card } from '../stores/board'

const props = defineProps<{ card: Card }>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'updated', card: Card): void
  (e: 'deleted', id: number): void
}>()

interface User { id: number; email: string; role: string }
interface Comment { id: number; text: string; author_id: number; created_at: string }
interface HistoryItem { id: number; action: string; user_id: number | null; created_at: string }

const title = ref(props.card.title)
const description = ref(props.card.description || '')
const priority = ref(props.card.priority)
const assigneeId = ref<number | null>(props.card.assignee_id)
const deadline = ref<string>(props.card.deadline ? props.card.deadline.slice(0, 10) : '')

const users = ref<User[]>([])
const comments = ref<Comment[]>([])
const history = ref<HistoryItem[]>([])
const newComment = ref('')
const error = ref('')
const saving = ref(false)
const activeTab = ref<'comments' | 'history'>('comments')

const priorities = [
  { value: 'low', label: 'Низкий' },
  { value: 'medium', label: 'Средний' },
  { value: 'high', label: 'Высокий' },
  { value: 'critical', label: 'Критический' },
]

async function load() {
  try {
    const [u, c, h] = await Promise.all([
      api.get('/auth/users').then((r) => r.data),
      api.get(`/cards/${props.card.id}/comments`).then((r) => r.data),
      api.get(`/cards/${props.card.id}/history`).then((r) => r.data),
    ])
    users.value = u
    comments.value = c
    history.value = h
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Ошибка загрузки'
  }
}

async function save() {
  saving.value = true
  error.value = ''
  try {
    const payload: any = {
      title: title.value,
      description: description.value || null,
      priority: priority.value,
      assignee_id: assigneeId.value,
      deadline: deadline.value ? new Date(deadline.value).toISOString() : null,
    }
    const { data } = await api.patch(`/cards/${props.card.id}`, payload)
    emit('updated', data)
    emit('close')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
}

async function remove() {
  if (!confirm('Удалить карточку?')) return
  try {
    await api.delete(`/cards/${props.card.id}`)
    emit('deleted', props.card.id)
    emit('close')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Ошибка удаления'
  }
}

async function addComment() {
  if (!newComment.value.trim()) return
  try {
    const { data } = await api.post(`/cards/${props.card.id}/comments`, { text: newComment.value })
    comments.value.push(data)
    newComment.value = ''
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Ошибка'
  }
}

function userName(id: number | null) {
  if (id === null) return '—'
  const u = users.value.find((x) => x.id === id)
  return u?.email || `#${id}`
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' })
}

function getInitials(email: string | undefined) {
  if (!email) return '?'
  return email.split('@')[0].slice(0, 2).toUpperCase()
}

onMounted(load)
</script>

<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <div class="modal-header-left">
          <span class="card-id">#{{ card.id }}</span>
          <span class="priority-pill" :class="priority">{{ priorities.find(p => p.value === priority)?.label }}</span>
        </div>
        <div class="modal-header-actions">
          <button class="btn-icon" @click="remove" title="Удалить">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M6 6l1 14a2 2 0 002 2h6a2 2 0 002-2l1-14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
          <button class="btn-icon" @click="$emit('close')" title="Закрыть">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="modal-body">
        <div class="main-col">
          <input v-model="title" class="title-input" placeholder="Заголовок" />

          <div class="field">
            <label class="field-label">Описание</label>
            <textarea v-model="description" rows="4" placeholder="Добавьте более подробное описание..." />
          </div>

          <div class="tabs">
            <button :class="{ active: activeTab === 'comments' }" @click="activeTab = 'comments'">
              Комментарии <span class="tab-count">{{ comments.length }}</span>
            </button>
            <button :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">
              История <span class="tab-count">{{ history.length }}</span>
            </button>
          </div>

          <div v-if="activeTab === 'comments'" class="comments">
            <div v-for="c in comments" :key="c.id" class="comment">
              <div class="comment-avatar">{{ getInitials(userName(c.author_id)) }}</div>
              <div class="comment-body">
                <div class="comment-head">
                  <strong>{{ userName(c.author_id) }}</strong>
                  <span class="time">{{ formatDate(c.created_at) }}</span>
                </div>
                <div class="comment-text">{{ c.text }}</div>
              </div>
            </div>
            <div v-if="comments.length === 0" class="empty">Комментариев пока нет</div>

            <div class="add-comment">
              <textarea v-model="newComment" rows="2" placeholder="Написать комментарий..." />
              <button class="btn" @click="addComment" :disabled="!newComment.trim()">Отправить</button>
            </div>
          </div>

          <div v-else class="history">
            <div v-for="h in history" :key="h.id" class="history-item">
              <div class="history-dot"></div>
              <div class="history-content">
                <div class="history-line">
                  <strong>{{ userName(h.user_id) }}</strong>
                  <span class="action">{{ h.action }}</span>
                </div>
                <span class="time">{{ formatDate(h.created_at) }}</span>
              </div>
            </div>
            <div v-if="history.length === 0" class="empty">Пока нет изменений</div>
          </div>
        </div>

        <div class="side-col">
          <div class="field">
            <label class="field-label">Приоритет</label>
            <select v-model="priority">
              <option v-for="p in priorities" :key="p.value" :value="p.value">{{ p.label }}</option>
            </select>
          </div>

          <div class="field">
            <label class="field-label">Исполнитель</label>
            <select v-model="assigneeId">
              <option :value="null">Не назначен</option>
              <option v-for="u in users" :key="u.id" :value="u.id">{{ u.email }}</option>
            </select>
          </div>

          <div class="field">
            <label class="field-label">Дедлайн</label>
            <input v-model="deadline" type="date" />
          </div>

          <div class="side-actions">
            <button class="btn" :disabled="saving" @click="save">
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <button class="btn btn-secondary" @click="$emit('close')">Отмена</button>
          </div>

          <p class="error" v-if="error">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(9, 30, 66, 0.54);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 48px 20px;
  z-index: 100;
  overflow-y: auto;
  animation: fadeIn 0.15s ease-out;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal {
  background: white;
  border-radius: 8px;
  width: 960px;
  max-width: 100%;
  box-shadow: 0 12px 40px rgba(9, 30, 66, 0.5);
  animation: slideUp 0.2s ease-out;
}
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebecf0;
}
.modal-header-left { display: flex; align-items: center; gap: 12px; }
.modal-header-actions { display: flex; gap: 4px; }

.card-id { font-size: 13px; color: #6b778c; font-weight: 600; }
.priority-pill {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.priority-pill.low { background: #e3fcef; color: #006644; }
.priority-pill.medium { background: #deebff; color: #0747a6; }
.priority-pill.high { background: #fff0b3; color: #974f0c; }
.priority-pill.critical { background: #ffebe6; color: #bf2600; }

.btn-icon {
  background: transparent;
  border: none;
  width: 32px; height: 32px;
  border-radius: 3px;
  display: flex; align-items: center; justify-content: center;
  color: #6b778c;
  transition: background 0.15s, color 0.15s;
}
.btn-icon:hover { background: rgba(9,30,66,0.08); color: #172b4d; }

.modal-body { display: flex; gap: 24px; padding: 24px; }
.main-col { flex: 1; display: flex; flex-direction: column; gap: 18px; min-width: 0; }
.side-col { width: 260px; display: flex; flex-direction: column; gap: 16px; flex-shrink: 0; }

.title-input {
  font-size: 20px;
  font-weight: 600;
  border: 2px solid transparent;
  padding: 8px 10px;
  border-radius: 4px;
  background: transparent;
}
.title-input:hover { background: #f4f5f7; }
.title-input:focus { border-color: #4c9aff; background: white; }

.field { display: flex; flex-direction: column; gap: 6px; }
.field-label {
  font-size: 11px;
  font-weight: 700;
  color: #6b778c;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tabs { display: flex; gap: 4px; border-bottom: 1px solid #ebecf0; }
.tabs button {
  background: none;
  border: none;
  padding: 8px 14px;
  font-size: 13px;
  color: #6b778c;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  margin-bottom: -1px;
}
.tabs button:hover { color: #172b4d; }
.tabs button.active { color: #0052cc; border-bottom-color: #0052cc; font-weight: 600; }
.tab-count {
  background: rgba(9,30,66,0.08);
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 11px;
  margin-left: 4px;
}

.comments, .history { display: flex; flex-direction: column; gap: 12px; }

.comment { display: flex; gap: 10px; }
.comment-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4c9aff, #0052cc);
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700;
  flex-shrink: 0;
}
.comment-body { flex: 1; background: #f4f5f7; padding: 10px 12px; border-radius: 6px; }
.comment-head { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px; }
.comment-text { font-size: 14px; color: #172b4d; line-height: 1.5; }

.add-comment { display: flex; flex-direction: column; gap: 8px; margin-top: 8px; }

.history-item { display: flex; gap: 12px; padding: 6px 0; }
.history-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #4c9aff;
  margin-top: 6px;
  flex-shrink: 0;
}
.history-content { flex: 1; }
.history-line { font-size: 13px; display: flex; gap: 6px; }
.history-line .action { color: #172b4d; }

.time { color: #97a0af; font-size: 11px; }

.side-actions { display: flex; flex-direction: column; gap: 8px; margin-top: auto; }
.error { color: #de350b; font-size: 12px; }
.empty { color: #97a0af; font-size: 13px; text-align: center; padding: 16px; font-style: italic; }
</style>