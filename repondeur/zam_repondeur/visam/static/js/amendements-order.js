class AmendementsOrder extends BaseOrder {
  static get targets() {
    return ['amendement']
  }

  dragstart(event) {
    super.dragstart(event)
    event.dataTransfer.setData('application/drag-num', event.target.dataset.num)
  }
  currentOrder() {
    return this.amendementTargets.map(amendement => amendement.dataset.num)
  }

  // Actual reordering on drop.
  drop(event) {
    event.preventDefault()
    const dropTarget = this.targetElement(event)

    const num = event.dataTransfer.getData('application/drag-num')
    const draggedItem = this.element.querySelector(`[data-num='${num}']`)

    // https://developer.mozilla.org/en-US/docs/Web/API/Node/compareDocumentPosition
    const positionComparison = dropTarget.compareDocumentPosition(draggedItem)
    if (positionComparison & Node.DOCUMENT_POSITION_FOLLOWING) {
      dropTarget.insertAdjacentElement('beforebegin', draggedItem)
    } else if (positionComparison & Node.DOCUMENT_POSITION_PRECEDING) {
      dropTarget.insertAdjacentElement('afterend', draggedItem)
    }

    const initialOrder = this.initialOrder(event)
    const currentOrder = this.currentOrder()
    if (!this.sameArrays(initialOrder, currentOrder))
      this.submitOrder(currentOrder)
  }
}

application.register('amendements-order', AmendementsOrder)
