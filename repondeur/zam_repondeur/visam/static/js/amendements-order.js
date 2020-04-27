class AmendementsOrder extends Stimulus.Controller {
  static get targets() {
    return ['parent', 'dropzone', 'amendement']
  }

  dragging(event) {
    // Necessary to start the dragging stuff.
  }
  registerDragged(event) {
    this.dragged = event.target
    this.draggedPreviousDropzone = event.target.previousElementSibling
    this.draggedNextDropzone = event.target.nextElementSibling
  }
  preventDefault(event) {
    event.preventDefault()
  }

  // Dropzones management.
  showDropzones(event) {
    this.dropzoneTargets.forEach(dropzone => {
      dropzone.classList.add('highlighted')
    })
    this.draggedPreviousDropzone.classList.remove('highlighted')
    this.draggedNextDropzone.classList.remove('highlighted')
    this.dragged.classList.add('highlighted')
    this.dragged.style.cursor = 'row-resize'
  }
  highlightDropzone(event) {
    if (event.target.parentElement.className.includes('dropzone')) {
      event.target.parentElement.classList.add('hover')
    }
  }
  downlightDropzone(event) {
    if (event.target.parentElement.className.includes('dropzone')) {
      event.target.parentElement.classList.remove('hover')
    }
  }
  hideDropzones(event) {
    this.dropzoneTargets.forEach(dropzone => {
      dropzone.classList.remove('highlighted')
      dropzone.classList.remove('hover')
    })
    this.dragged.classList.remove('highlighted')
    this.dragged.style.cursor = 'auto'
  }

  // Actual reordering on drop.
  reorder(event) {
    const nextSibling = event.target.parentElement.nextElementSibling
    this.parentTarget.removeChild(this.dragged)
    this.parentTarget.removeChild(this.draggedNextDropzone)
    const newDragged = this.parentTarget.insertBefore(this.dragged, nextSibling)
    this.parentTarget.insertBefore(this.draggedNextDropzone, nextSibling)
    const newOrder = this.amendementTargets.map(
      amendement => amendement.dataset.num
    )
    this.submitOrder(newOrder)
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

application.register('amendements-order', AmendementsOrder)