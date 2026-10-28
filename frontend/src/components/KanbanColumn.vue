<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import draggable from 'vuedraggable'
import KanbanCard from './KanbanCard.vue'
import type { Card, Column } from '../stores/board'

const props = defineProps<{ column: Column; cards: Card[] }>()
const emit = defineEmits<{
  (e: 'add-card', columnId: number, title: string): void
  (e: 'delete-card', id: number): void
  (e: 'change', columnId: number, cards: Card[]): void
  (e: 'open-card', card: Card): void
}>()

const newTitle = ref('')
const showAddForm = ref(false)
const localCards = ref<Card[]>([...props.cards])

watch(() => props.cards, (newCards) => {
  localCards.value = [...newCards]
}, { deep: true })

const isOverLimit = computed(() =>
  props.column.wip_limit !== null && props.cards.length >= props.column.wip_limit
)

function onAdd() {
  if (!newTitle.value.trim()) return
  emit('add-card', props.column.id, newTitle.value)
  newTitle.value = ''
  showAddForm.value = false
}

function onChange() {
  emit('change', props.column.id, localCards.value)
}
</script>

<template>
  <div class="kanban-column">
    <div class="col-header">
      <div class="col-title-row">
        <span class="col-name">{{ column.name }}</span>
        <span class="col-count">{{ cards.length }}</span>
        <span
          v-if="column.wip_limit"
          class="wip-badge"
          :class="{ 'wip-warn': isOverLimit }"
          :title="`Лимит карточек: ${column.wip_limit}`"
        >
          Лимит {{ cards.length }}/{{ column.wip_limit }}
        </span>
      </div>
    </div>

    <draggable
      v-model="localCards"
      item-key="id"
      group="cards"
      class="cards-list"
      :animation="180"
      ghost-class="ghost-card"
      drag-class="drag-card"
      @change="onChange"
    >
      <template #item="{ element }">
        <KanbanCard
          :card="element"
          @delete="$emit('delete-card', element.id)"
          @open="$emit('open-card', element)"
        />
      </template>
      <template #footer>
        <div v-if="localCards.length === 0" class="empty-state">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" opacity="0.4">
            <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" stroke-width="1.5" stroke-dasharray="3 3"/>
          </svg>
          <span>Перетащите карточку сюда</span>
        </div>
      </template>
    </draggable>

    <div class="add-row">
      <button v-if="!showAddForm" class="add-card-btn" @click="showAddForm = true">
        <span>+</span> Добавить карточку
      </button>
      <div v-else class="add-card-form">
        <input
          v-model="newTitle"
          placeholder="Введите название..."
          @keyup.enter="onAdd"
          @keyup.esc="showAddForm = false"
          autofocus
        />
        <div class="add-card-actions">
          <button class="btn" @click="onAdd">Добавить</button>
          <button class="btn-icon" @click="showAddForm = false" title="Отмена">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.kanban-column {
  background: #ebecf0;
  border-radius: 12px;
  padding: 10px;
  width: 300px;
  min-width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 240px);
  box-shadow: 0 1px 2px rgba(9, 30, 66, 0.08), 0 0 1px rgba(9, 30, 66, 0.15);
  transition: box-shadow 0.2s;
}
.kanban-column:hover {
  box-shadow: 0 2px 8px rgba(9, 30, 66, 0.12), 0 0 1px rgba(9, 30, 66, 0.15);
}

.col-header { padding: 6px 8px 12px; }
.col-title-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.col-name { font-weight: 700; font-size: 13px; color: #172b4d; text-transform: uppercase; letter-spacing: 0.4px; }
.col-count {
  font-size: 11px;
  color: #6b778c;
  background: rgba(9,30,66,0.08);
  padding: 1px 7px;
  border-radius: 10px;
  font-weight: 700;
}
.wip-badge {
  font-size: 10px;
  color: #6b778c;
  background: rgba(9,30,66,0.06);
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}
.wip-warn { background: #ffebe6; color: #de350b; font-weight: 700; }

.cards-list {
  min-height: 20px;
  overflow-y: auto;
  flex: 1;
  padding: 2px 2px 4px;
  margin: 0 -2px;
}

.ghost-card { opacity: 0.4; background: #c1c7d0; border-radius: 8px; }
.drag-card { transform: rotate(3deg); box-shadow: 0 8px 16px rgba(9,30,66,0.3); }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 28px 12px;
  color: #97a0af;
  font-size: 12px;
  border: 2px dashed #dfe1e6;
  border-radius: 10px;
  margin: 4px 2px;
}

.add-row { margin-top: 8px; padding: 0 2px; }
.add-card-btn {
  width: 100%;
  background: transparent;
  border: none;
  padding: 8px 10px;
  text-align: left;
  font-size: 13px;
  color: #6b778c;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background 0.15s, color 0.15s;
}
.add-card-btn:hover { background: rgba(9,30,66,0.08); color: #172b4d; }
.add-card-btn span { font-size: 18px; line-height: 1; }

.add-card-form { display: flex; flex-direction: column; gap: 8px; }
.add-card-form input { font-size: 13px; border-radius: 6px; }
.add-card-actions { display: flex; gap: 6px; align-items: center; }
</style>