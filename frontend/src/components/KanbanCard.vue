<script setup lang="ts">
import { computed } from 'vue'
import type { Card } from '../stores/board'

const props = defineProps<{ card: Card }>()
const emit = defineEmits<{
  (e: 'delete', id: number): void
  (e: 'open', card: Card): void
}>()

const priorityLabel = computed(() => {
  const map: Record<string, string> = {
    low: 'Низкий',
    medium: 'Средний',
    high: 'Высокий',
    critical: 'Критический',
  }
  return map[props.card.priority] || props.card.priority
})

const assigneeInitials = computed(() => {
  const email = (props.card as any).assignee_email
  if (email) {
    const name = email.split('@')[0]
    return name.slice(0, 2).toUpperCase()
  }
  if (props.card.assignee_id) return `U${props.card.assignee_id}`
  return null
})

const assigneeTitle = computed(() => {
  return (props.card as any).assignee_email || (props.card.assignee_id ? `Пользователь #${props.card.assignee_id}` : '')
})

const isOverdue = computed(() => {
  if (!props.card.deadline) return false
  return new Date(props.card.deadline) < new Date()
})

const deadlineLabel = computed(() => {
  if (!props.card.deadline) return ''
  return new Date(props.card.deadline).toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' })
})
</script>

<template>
  <div class="kanban-card" :class="`p-${card.priority}`" @click="emit('open', card)">
    <div class="card-priority-bar" :class="card.priority"></div>
    <div class="card-body">
      <div class="card-title">{{ card.title }}</div>

      <div class="card-footer">
        <div class="card-badges">
          <span v-if="card.deadline" class="badge" :class="{ overdue: isOverdue }">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="5" width="18" height="16" rx="2" stroke="currentColor" stroke-width="2"/>
              <path d="M3 9h18M8 3v4M16 3v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            {{ deadlineLabel }}
          </span>
          <span class="badge priority-badge" :class="card.priority">{{ priorityLabel }}</span>
        </div>

        <div class="card-right">
          <div v-if="assigneeInitials" class="assignee-avatar" :title="assigneeTitle">
            {{ assigneeInitials }}
          </div>
          <button class="del" @click.stop="emit('delete', card.id)" title="Удалить">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.kanban-card {
  position: relative;
  display: flex;
  background: white;
  border-radius: 10px;
  margin-bottom: 8px;
  box-shadow: 0 1px 2px rgba(9, 30, 66, 0.12), 0 0 0 1px rgba(9, 30, 66, 0.04);
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s, background 0.15s;
  user-select: none;
  overflow: hidden;
}
.kanban-card:hover {
  box-shadow: 0 4px 12px rgba(9, 30, 66, 0.18), 0 0 0 1px rgba(9, 30, 66, 0.08);
  background: white;
  transform: translateY(-2px);
}
.kanban-card:active { cursor: grabbing; transform: translateY(0); }

.card-priority-bar { width: 4px; flex-shrink: 0; }
.card-priority-bar.low { background: #36b37e; }
.card-priority-bar.medium { background: #4c9aff; }
.card-priority-bar.high { background: #ffab00; }
.card-priority-bar.critical { background: #de350b; }

.card-body { flex: 1; padding: 12px 14px; min-width: 0; }

.card-title {
  font-size: 14px;
  line-height: 1.5;
  color: #172b4d;
  word-break: break-word;
  margin-bottom: 10px;
  font-weight: 500;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.card-badges { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }

.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  background: #f4f5f7;
  color: #42526e;
  border-radius: 6px;
  white-space: nowrap;
}
.badge.overdue { background: #ffebe6; color: #bf2600; }

.priority-badge.low { background: #e3fcef; color: #006644; }
.priority-badge.medium { background: #deebff; color: #0747a6; }
.priority-badge.high { background: #fff0b3; color: #974f0c; }
.priority-badge.critical { background: #ffebe6; color: #bf2600; }

.card-right { display: flex; align-items: center; gap: 4px; }
.assignee-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4c9aff, #0052cc);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  box-shadow: 0 0 0 2px white;
}

.del {
  background: none;
  border: none;
  color: #6b778c;
  padding: 5px;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.15s, background 0.15s, color 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.kanban-card:hover .del { opacity: 1; }
.del:hover { background: #ffebe6; color: #de350b; }
</style>