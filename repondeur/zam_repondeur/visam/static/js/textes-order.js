class TextesOrder extends BaseOrder {
  static get targets() {
    return ['texte']
  }

  dragstart(event) {
    super.dragstart(event)
    event.dataTransfer.setData('application/drag-pk', event.target.dataset.pk)
  }

  currentOrder() {
    return this.texteTargets.map(texte => texte.dataset.pk)
  }

  // Actual reordering on drop.
  drop(event) {
    event.preventDefault()
    const dropTarget = this.targetElement(event)

    const pk = event.dataTransfer.getData('application/drag-pk')
    const draggedItem = this.element.querySelector(`[data-pk='${pk}']`)

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

application.register('textes-order', TextesOrder)
