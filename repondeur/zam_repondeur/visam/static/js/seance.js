class BaseOrder extends Stimulus.Controller {
  dragstart(event) {
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
      this.targetElement(event).classList.add('drag-over')
    }
  }
  dragleave(event) {
    this.removeDragOver()
  }
  dragend(event) {
    event.target.classList.remove('highlighted')
    this.removeDragOver()
  }

  initialOrder(event) {
    return event.dataTransfer.getData('application/initial-order').split(',')
  }
  removeDragOver(event) {
    Array.from(this.element.querySelectorAll('.drag-over')).forEach(element =>
      element.classList.remove('drag-over')
    )
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
  targetElement(event) {
    const target = event.target
    if (this.isDraggable(target)) {
      return target
    }
    const parent = target.parentElement
    if (this.isDraggable(parent)) {
      return parent
    }
    const grandParent = parent.parentElement
    if (this.isDraggable(grandParent)) {
      return grandParent
    }
    return false
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
