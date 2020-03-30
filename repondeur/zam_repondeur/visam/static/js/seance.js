class TextesOrder extends Stimulus.Controller {
  static get targets() {
    return ['texte']
  }

  dragstart(event) {
    event.dataTransfer.setData('application/drag-pk', event.target.dataset.pk)
    event.dataTransfer.setData('application/initial-order', this.currentOrder())
    event.dataTransfer.effectAllowed = 'move'
    event.target.classList.add('highlighted')
  }
  dragenter(event) {
    if (this.isDropZone(event)) {
      event.preventDefault()
    }
  }
  dragover(event) {
    event.dataTransfer.dropEffect = 'move'
    if (this.isDropZone(event)) {
      event.preventDefault()
    }
  }
  dragend(event) {
    event.target.classList.remove('highlighted')
  }

  initialOrder(event) {
    return event.dataTransfer.getData('application/initial-order').split(',')
  }
  currentOrder() {
    return this.texteTargets.map(texte => texte.dataset.pk)
  }
  sameArrays(array1, array2) {
    // Full credits to https://stackoverflow.com/a/19746771
    return (
      array1.length === array2.length &&
      array1.every((value, index) => value === array2[index])
    )
  }
  isDraggable(element) {
    if (!(element instanceof HTMLElement)) {
      element = element.parentElement
    }
    return (
      element.hasAttribute('draggable') &&
      element.getAttribute('draggable') == 'true'
    )
  }
  isDropZone(event) {
    return (
      this.isDraggable(event.target) ||
      this.isDraggable(event.target.parentElement) ||
      this.isDraggable(event.target.parentElement.parentElement)
    )
  }
  texteElement(event) {
    const target = event.target
    if (this.isDraggable(target)) {
      return target
    }
    const parent = target.parentElement
    if (this.isDraggable(parent)) {
      return parent
    }
    return false
  }

  // Actual reordering on drop.
  drop(event) {
    event.preventDefault()
    const dropTarget = this.texteElement(event)

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

  XHROptions() {
    const headers = new Headers({
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/json'
    })
    return {
      method: 'POST',
      credentials: 'include',
      headers: headers
    }
  }

  submitOrder(order) {
    const options = this.XHROptions()
    options['body'] = JSON.stringify({
      order: order
    })
    fetch(this.data.get('url'), options)
  }
}

application.register('textes-order', TextesOrder)
