<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/client'
import { useBoardStore } from '../stores/board'
import { useAuthStore } from '../stores/auth'
import KanbanColumn from '../components/KanbanColumn.vue'
import CardModal from '../components/CardModal.vue'
import type { Card } from '../stores/board'

const route = useRoute()
const router = useRouter()
const boardId = Number(route.params.id)
const store = useBoardStore()
const auth = useAuthStore()
const newColName = ref('')
const newColWip = ref<number | null>(null)
const error = ref('')

interface BoardDetails {
  id: number
  name: string
  project_id: number
  project: { id: number; name: string } | null
}
const board = ref<BoardDetails | null>(null)
const selectedCard = ref<Card | null>(null)

const filterText = ref('')
const filterPriority = ref<string>('')
const filterAssignee = ref<string>('')
const filterDeadline = ref<string>('')

const priorities = [
  { value: '', label: 'Все приоритеты' },
  { value: 'low', label: 'Низкий' },
  { value: 'medium', label: 'Средний' },
  { value: 'high', label: 'Высокий' },
  { value: 'critical', label: 'Критический' },
]

const assigneeOptions = computed(() => {
  const ids = new Set<number>()
  store.cards.forEach((c) => {
    if (c.assignee_id !== null) ids.add(c.assignee_id)
  })
  return Array.from(ids).map((id) => {
    const card = store.cards.find((c) => c.assignee_id === id)
    return {
      value: String(id),
      label: (card as any)?.assignee_email || `Пользователь #${id}`,
    }
  })
})

const deadlineOptions = [
  { value: '', label: 'Все дедлайны' },
  { value: 'overdue', label: 'Просроченные' },
  { value: 'week', label: 'Ближайшие 7 дней' },
  { value: 'none', label: 'Без дедлайна' },
]

const userInitials = computed(() => {
  const email = auth.user?.email || ''
  return email.split('@')[0].slice(0, 2).toUpperCase()
})

const roleLabel = computed(() => {
  const r = auth.user?.role
  if (r === 'admin') return 'Администратор'
  if (r === 'manager') return 'Менеджер'
  if (r === 'developer') return 'Разработчик'
  return r || ''
})

const canManage = computed(() => auth.user?.role !== 'developer')

const hasActiveFilters = computed(
  () => filterText.value || filterPriority.value || filterAssignee.value || filterDeadline.value
)

const activeFilterCount = computed(() => {
  let n = 0
  if (filterText.value) n++
  if (filterPriority.value) n++
  if (filterAssignee.value) n++
  if (filterDeadline.value) n++
  return n
})

function resetFilters() {
  filterText.value = ''
  filterPriority.value = ''
  filterAssignee.value = ''
  filterDeadline.value = ''
}

function matchesFilters(card: Card): boolean {
  if (filterText.value) {
    const q = filterText.value.toLowerCase()
    const hay = `${card.title} ${card.description || ''}`.toLowerCase()
    if (!hay.includes(q)) return false
  }
  if (filterPriority.value && card.priority !== filterPriority.value) return false
  if (filterAssignee.value) {
    if (filterAssignee.value === 'none') {
      if (card.assignee_id !== null) return false
    } else if (card.assignee_id !== Number(filterAssignee.value)) {
      return false
    }
  }
  if (filterDeadline.value) {
    if (filterDeadline.value === 'none') {
      if (card.deadline !== null) return false
    } else if (filterDeadline.value === 'overdue') {
      if (!card.deadline || new Date(card.deadline) >= new Date()) return false
    } else if (filterDeadline.value === 'week') {
      if (!card.deadline) return false
      const d = new Date(card.deadline)
      const now = new Date()
      const week = new Date()
      week.setDate(now.getDate() + 7)
      if (d < now || d > week) return false
    }
  }
  return true
}

function cardsForColumn(columnId: number): Card[] {
  return store.cardsInColumn(columnId).filter(matchesFilters)
}

const totalVisible = computed(() => store.cards.filter(matchesFilters).length)

async function load() {
  try {
    const [boardData] = await Promise.all([
      api.get(`/boards/${boardId}/details`).then((r) => r.data),
      store.loadBoard(boardId),
    ])
    board.value = boardData
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Ошибка загрузки'
  }
}

function goToProject() {
  if (board.value?.project_id) {
    router.push('/projects')
  }
}

async function addColumn() {
  if (!newColName.value.trim()) return
  try {
    await store.createColumn(boardId, newColName.value, newColWip.value || null)
    newColName.value = ''
    newColWip.value = null
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Ошибка'
  }
}

async function addCard(columnId: number, title: string) {
  try {
    await store.createCard(columnId, title)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Ошибка'
  }
}

async function removeCard(id: number) {
  await store.deleteCard(id)
}

async function onColumnChange(columnId: number, cards: Card[]) {
  for (let i = 0; i < cards.length; i++) {
    const c = cards[i]
    if (c.column_id !== columnId || c.order !== i) {
      try {
        await store.moveCard(c.id, columnId, i)
      } catch (e: any) {
        error.value = e.response?.data?.detail || 'Ошибка перемещения'
        await load()
        return
      }
    }
  }
}

function openCard(card: Card) {
  selectedCard.value = card
}
function closeCard() {
  selectedCard.value = null
}
function onCardUpdated(card: Card) {
  const idx = store.cards.findIndex((c) => c.id === card.id)
  if (idx !== -1) store.cards[idx] = card
  selectedCard.value = null
}
function onCardDeleted(id: number) {
  store.cards = store.cards.filter((c) => c.id !== id)
  selectedCard.value = null
}
function logout() {
  auth.logout()
  router.push('/login')
}

watch(() => store.cards, () => {}, { deep: true })
onMounted(load)
</script>

<template>
  <div class="page">
    <!-- Верхний топбар -->
    <header class="topbar">
      <div class="topbar-left">
        <div class="logo">
          <div class="logo-mark">K</div>
        </div>
        <nav class="breadcrumbs" v-if="board">
          <router-link to="/projects" class="crumb">Проекты</router-link>
          <svg class="crumb-sep" width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <a class="crumb" @click.prevent="goToProject">{{ board.project?.name || 'Проект' }}</a>
          <svg class="crumb-sep" width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span class="crumb current">{{ board.name }}</span>
        </nav>
      </div>
      <div class="topbar-right">
        <button class="btn-icon-light" title="Поиск">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/>
            <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
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

    <!-- Подшапка доски -->
    <div class="board-subheader">
      <div class="board-subheader-left">
        <div class="board-title-block">
          <h1 class="board-title">{{ board?.name || 'Доска' }}</h1>
          <div class="board-meta">
            <span v-if="board?.project" class="meta-item">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="4" width="7" height="16" rx="1.5" stroke="currentColor" stroke-width="2"/>
                <rect x="14" y="4" width="7" height="10" rx="1.5" stroke="currentColor" stroke-width="2"/>
              </svg>
              {{ board.project.name }}
            </span>
            <span class="meta-dot">•</span>
            <span class="meta-item">{{ store.columns.length }} колонок</span>
            <span class="meta-dot">•</span>
            <span class="meta-item">{{ totalVisible }} из {{ store.cards.length }} карточек</span>
          </div>
        </div>
      </div>
      <div class="board-subheader-right">
        <button class="btn-icon" title="Поделиться">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <circle cx="18" cy="5" r="3" stroke="currentColor" stroke-width="2"/>
            <circle cx="6" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
            <circle cx="18" cy="19" r="3" stroke="currentColor" stroke-width="2"/>
            <path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
        <button class="btn-icon" title="Настройки">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
            <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
        <div class="board-avatars">
          <div class="board-avatar">{{ userInitials }}</div>
        </div>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="filters-bar">
      <div class="filter-search-wrapper">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/>
          <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <input v-model="filterText" class="filter-search" placeholder="Поиск карточек..." />
      </div>
      <select v-model="filterPriority" class="filter-select">
        <option v-for="p in priorities" :key="p.value" :value="p.value">{{ p.label }}</option>
      </select>
      <select v-model="filterAssignee" class="filter-select">
        <option value="">Все исполнители</option>
        <option value="none">Без исполнителя</option>
        <option v-for="u in assigneeOptions" :key="u.value" :value="u.value">{{ u.label }}</option>
      </select>
      <select v-model="filterDeadline" class="filter-select">
        <option v-for="d in deadlineOptions" :key="d.value" :value="d.value">{{ d.label }}</option>
      </select>
      <button v-if="hasActiveFilters" class="btn btn-secondary filter-reset" @click="resetFilters">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
          <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        Сбросить ({{ activeFilterCount }})
      </button>
    </div>

    <p class="error" v-if="error">{{ error }}</p>

    <!-- Доска -->
    <main class="board">
      <KanbanColumn
        v-for="col in store.columns"
        :key="col.id"
        :column="col"
        :cards="cardsForColumn(col.id)"
        @add-card="addCard"
        @delete-card="removeCard"
        @change="onColumnChange"
        @open-card="openCard"
      />
      <div class="add-column" v-if="canManage">
        <div class="add-col-title">Новая колонка</div>
        <input v-model="newColName" placeholder="Название" />
        <input v-model.number="newColWip" type="number" placeholder="Лимит карточек" min="1" />
        <button class="btn" @click="addColumn">+ Добавить</button>
      </div>
    </main>

    <CardModal
      v-if="selectedCard"
      :card="selectedCard"
      @close="closeCard"
      @updated="onCardUpdated"
      @deleted="onCardDeleted"
    />
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f4f5f7;
}

/* Топбар */
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 52px;
  background: #0747a6;
  color: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
  position: relative;
  z-index: 10;
}
.topbar-left { display: flex; align-items: center; gap: 16px; min-width: 0; }
.topbar-right { display: flex; align-items: center; gap: 10px; }

.logo-mark {
  width: 28px; height: 28px; border-radius: 6px;
  background: rgba(255,255,255,0.2);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  min-width: 0;
}
.crumb {
  color: rgba(255,255,255,0.8);
  text-decoration: none;
  padding: 4px 8px;
  border-radius: 3px;
  transition: background 0.15s, color 0.15s;
  cursor: pointer;
  white-space: nowrap;
}
.crumb:hover { background: rgba(255,255,255,0.15); color: white; }
.crumb.current {
  color: white;
  font-weight: 600;
  cursor: default;
}
.crumb.current:hover { background: transparent; }
.crumb-sep { color: rgba(255,255,255,0.4); flex-shrink: 0; }

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
  display: flex; align-items: center; gap: 8px;
  padding: 3px 10px 3px 3px;
  background: rgba(255,255,255,0.12);
  border-radius: 20px;
}
.avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: #4c9aff;
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 11px;
  box-shadow: 0 0 0 2px rgba(255,255,255,0.3);
}
.user-info { display: flex; flex-direction: column; line-height: 1.2; }
.user-email { font-size: 11px; font-weight: 500; }
.user-role { font-size: 10px; color: rgba(255,255,255,0.7); }

/* Подшапка доски */
.board-subheader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 14px;
  gap: 16px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}
.board-subheader-left { min-width: 0; flex: 1; }
.board-title-block { display: flex; flex-direction: column; gap: 4px; }
.board-title { font-size: 22px; font-weight: 700; color: #172b4d; }

.board-meta { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #6b778c; flex-wrap: wrap; }
.meta-item { display: inline-flex; align-items: center; gap: 4px; }
.meta-dot { color: #c1c7d0; }

.board-subheader-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
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

.board-avatars { display: flex; margin-left: 4px; }
.board-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, #4c9aff, #0052cc);
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700;
  box-shadow: 0 0 0 2px white;
}

/* Фильтры */
.filters-bar {
  display: flex;
  gap: 8px;
  padding: 0 24px 16px;
  align-items: center;
  flex-wrap: wrap;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}
.filter-search-wrapper {
  position: relative;
  flex: 1;
  min-width: 200px;
  max-width: 320px;
}
.filter-search-wrapper svg {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b778c;
  pointer-events: none;
}
.filter-search { padding-left: 34px; width: 100%; }
.filter-select { min-width: 150px; }

.filter-reset {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  font-size: 13px;
}

/* Доска */
.board {
  display: flex;
  gap: 16px;
  padding: 0 24px 32px;
  overflow-x: auto;
  align-items: flex-start;
  flex: 1;
  justify-content: center;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

.add-column {
  background: rgba(9, 30, 66, 0.04);
  border-radius: 8px;
  padding: 12px;
  width: 288px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.add-col-title { font-size: 13px; font-weight: 600; color: #6b778c; margin-bottom: 4px; }

.error {
  color: #de350b;
  padding: 10px 16px;
  background: #ffebe6;
  margin: 0 auto 12px;
  border-radius: 8px;
  max-width: 1600px;
  width: calc(100% - 48px);
}
@media (max-width: 1400px) {
  .board { justify-content: flex-start; }
}
</style>