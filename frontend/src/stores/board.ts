import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api/client'

export interface Column {
  id: number
  name: string
  board_id: number
  order: number
  wip_limit: number | null
}

export interface Card {
  id: number
  title: string
  description: string | null
  column_id: number
  assignee_id: number | null
  priority: string
  deadline: string | null
  order: number
}

export const useBoardStore = defineStore('board', () => {
  const columns = ref<Column[]>([])
  const cards = ref<Card[]>([])

  async function loadBoard(boardId: number) {
    const { data: cols } = await api.get(`/boards/${boardId}/columns`)
    columns.value = cols
    const allCards: Card[] = []
    for (const col of cols) {
      const { data: colCards } = await api.get(`/columns/${col.id}/cards`)
      allCards.push(...colCards)
    }
    cards.value = allCards
  }

  async function createColumn(boardId: number, name: string, wip_limit: number | null) {
    const order = columns.value.length
    const { data } = await api.post(`/boards/${boardId}/columns`, { name, order, wip_limit })
    columns.value.push(data)
  }

  async function createCard(columnId: number, title: string) {
    const { data } = await api.post(`/columns/${columnId}/cards`, { title })
    cards.value.push(data)
  }

  async function moveCard(cardId: number, columnId: number, order: number) {
    const { data } = await api.patch(`/cards/${cardId}/move`, { column_id: columnId, order })
    const idx = cards.value.findIndex((c) => c.id === cardId)
    if (idx !== -1) cards.value[idx] = data
  }

  async function deleteCard(cardId: number) {
    await api.delete(`/cards/${cardId}`)
    cards.value = cards.value.filter((c) => c.id !== cardId)
  }

  function cardsInColumn(columnId: number) {
    return cards.value.filter((c) => c.column_id === columnId).sort((a, b) => a.order - b.order)
  }

  return { columns, cards, loadBoard, createColumn, createCard, moveCard, deleteCard, cardsInColumn }
})
