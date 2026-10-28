<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import { useAuthStore } from '../stores/auth'

interface Project { id: number; name: string; description: string | null; owner_id: number }
interface Board { id: number; name: string; project_id: number }

const projects = ref<Project[]>([])
const boards = ref<Record<number, Board[]>>({})
const newName = ref('')
const newDesc = ref('')
const error = ref('')
const showCreateForm = ref(false)
const auth = useAuthStore()
const router = useRouter()

const userInitials = computed(() => {
  const email = auth.user?.email || ''
  return email.slice(0, 2).toUpperCase()
})

const roleLabel = computed(() => {
  const r = auth.user?.role
  if (r === 'admin') return 'Администратор'
  if (r === 'manager') return 'Менеджер'
  if (r === 'developer') return 'Разработчик'
  return r || ''
})

const canManage = computed(() => auth.user?.role !== 'developer')

async function load() {
  const { data } = await api.get('/projects')
  projects.value = data
  for (const p of projects.value) {
    const { data: b } = await api.get(`/projects/${p.id}/boards`)
    boards.value[p.id] = b
  }
}

async function createProject() {
  if (!newName.value.trim()) return
  error.value = ''
  try {
    await api.post('/projects', { name: newName.value, description: newDesc.value })
    newName.value = ''
    newDesc.value = ''
    showCreateForm.value = false
    await load()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Ошибка'
  }
}

async function createBoard(projectId: number) {
  const name = prompt('Название доски')
  if (!name) return
  await api.post(`/projects/${projectId}/boards`, { name })
  await load()
}

async function deleteProject(id: number) {
  if (!confirm('Удалить проект?')) return
  await api.delete(`/projects/${id}`)
  await load()
}

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(load)
</script>

<template>
  <div class="page">
    <header class="topbar">
      <div class="topbar-left">
        <div class="logo">
          <div class="logo-mark">K</div>
          <span>Kanban</span>
        </div>
      </div>
      <div class="topbar-right">
        <div class="user-chip">
          <div class="avatar">{{ userInitials }}</div>
          <div class="user-info">
            <div class="user-email">{{ auth.user?.email }}</div>
            <div class="user-role">{{ roleLabel }}</div>
          </div>
        </div>
        <button class="btn-icon-light" @click="logout" title="Выйти">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </header>

    <main class="content">
      <div class="page-header">
        <div>
          <h1>Проекты</h1>
          <p class="subtitle">{{ projects.length }} {{ projects.length === 1 ? 'проект' : 'проектов' }}</p>
        </div>
        <button v-if="canManage" class="btn" @click="showCreateForm = !showCreateForm">
          <span class="btn-plus">+</span> Создать проект
        </button>
      </div>

      <div v-if="showCreateForm" class="create-form">
        <h3>Новый проект</h3>
        <input v-model="newName" placeholder="Название проекта" />
        <textarea v-model="newDesc" placeholder="Описание (опционально)" rows="2"></textarea>
        <div class="form-actions">
          <button class="btn" @click="createProject">Создать</button>
          <button class="btn btn-secondary" @click="showCreateForm = false">Отмена</button>
        </div>
        <p class="error" v-if="error">{{ error }}</p>
      </div>

      <div class="projects-grid">
        <div
          v-for="p in projects"
          :key="p.id"
          class="project-card"
        >
          <div class="project-head">
            <div class="project-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="4" width="7" height="16" rx="1.5" stroke="currentColor" stroke-width="2"/>
                <rect x="14" y="4" width="7" height="10" rx="1.5" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="project-title-block">
              <h3>{{ p.name }}</h3>
              <p class="desc">{{ p.description || 'Без описания' }}</p>
            </div>
            <button v-if="canManage" class="btn-icon danger" @click.stop="deleteProject(p.id)" title="Удалить">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M6 6l1 14a2 2 0 002 2h6a2 2 0 002-2l1-14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="boards-section">
            <div class="boards-label">Доски</div>
            <div class="boards">
              <div
                class="board-chip"
                v-for="b in boards[p.id]"
                :key="b.id"
                @click="router.push(`/boards/${b.id}`)"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
                  <path d="M9 3v18M15 3v18" stroke="currentColor" stroke-width="2"/>
                </svg>
                {{ b.name }}
              </div>
              <button v-if="canManage" class="board-add-btn" @click="createBoard(p.id)">
                <span>+</span> Доска
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="projects.length === 0" class="empty-page">
        <div class="empty-icon">📋</div>
        <h3>Пока нет проектов</h3>
        <p v-if="canManage">Создайте первый проект, чтобы начать работу</p>
        <p v-else>Обратитесь к менеджеру или администратору</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page { min-height: 100vh; display: flex; flex-direction: column; background: #f4f5f7; }

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 56px;
  background: linear-gradient(135deg, #0747a6 0%, #0052cc 100%);
  color: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
.topbar-left { display: flex; align-items: center; }
.logo { display: flex; align-items: center; gap: 10px; font-size: 16px; font-weight: 700; }
.logo-mark {
  width: 28px; height: 28px; border-radius: 6px;
  background: rgba(255,255,255,0.2);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px;
}
.topbar-right { display: flex; align-items: center; gap: 12px; }

.btn-icon-light {
  background: transparent;
  border: none;
  width: 32px; height: 32px;
  border-radius: 3px;
  display: flex; align-items: center; justify-content: center;
  color: white; opacity: 0.85;
  transition: background 0.15s, opacity 0.15s;
}
.btn-icon-light:hover { background: rgba(255,255,255,0.15); opacity: 1; }

.user-chip {
  display: flex; align-items: center; gap: 10px;
  padding: 4px 12px 4px 4px;
  background: rgba(255,255,255,0.12);
  border-radius: 20px;
}
.avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: #4c9aff;
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 12px;
  box-shadow: 0 0 0 2px rgba(255,255,255,0.3);
}
.user-info { display: flex; flex-direction: column; line-height: 1.2; }
.user-email { font-size: 12px; font-weight: 500; }
.user-role { font-size: 11px; color: rgba(255,255,255,0.7); }

.content { padding: 32px; max-width: 1200px; margin: 0 auto; width: 100%; flex: 1; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
}
.page-header h1 { font-size: 28px; font-weight: 700; color: #172b4d; }
.subtitle { color: #6b778c; font-size: 13px; margin-top: 4px; }
.btn-plus { font-size: 18px; line-height: 1; margin-right: 4px; }

.create-form {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(9,30,66,0.15);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.create-form h3 { font-size: 16px; margin-bottom: 4px; }
.form-actions { display: flex; gap: 8px; }
.error { color: #de350b; font-size: 13px; }

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.project-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(9,30,66,0.15);
  transition: box-shadow 0.15s, transform 0.15s;
}
.project-card:hover {
  box-shadow: 0 4px 12px rgba(9,30,66,0.2);
  transform: translateY(-2px);
}

.project-head { display: flex; gap: 12px; margin-bottom: 14px; align-items: flex-start; }
.project-icon {
  width: 40px; height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #4c9aff, #0052cc);
  color: white;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.project-title-block { flex: 1; min-width: 0; }
.project-title-block h3 { font-size: 16px; font-weight: 600; margin-bottom: 4px; color: #172b4d; }
.desc { font-size: 13px; color: #6b778c; line-height: 1.4; }

.btn-icon {
  background: transparent;
  border: none;
  width: 28px; height: 28px;
  border-radius: 3px;
  display: flex; align-items: center; justify-content: center;
  color: #6b778c;
  transition: background 0.15s, color 0.15s;
}
.btn-icon:hover { background: rgba(9,30,66,0.08); }
.btn-icon.danger:hover { background: #ffebe6; color: #de350b; }

.boards-section { padding-top: 12px; border-top: 1px solid #ebecf0; }
.boards-label { font-size: 11px; font-weight: 700; color: #6b778c; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.boards { display: flex; gap: 6px; flex-wrap: wrap; }

.board-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ebecf0;
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  color: #172b4d;
  transition: background 0.15s, transform 0.1s;
}
.board-chip:hover { background: #dfe1e6; transform: translateY(-1px); }

.board-add-btn {
  background: transparent;
  border: 2px dashed #dfe1e6;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 13px;
  color: #6b778c;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: border-color 0.15s, color 0.15s;
}
.board-add-btn:hover { border-color: #4c9aff; color: #0052cc; }
.board-add-btn span { font-size: 16px; line-height: 1; }

.empty-page {
  text-align: center;
  padding: 60px 20px;
  color: #6b778c;
}
.empty-icon { font-size: 48px; margin-bottom: 12px; opacity: 0.5; }
.empty-page h3 { font-size: 18px; color: #172b4d; margin-bottom: 6px; }
</style>