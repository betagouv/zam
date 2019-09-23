class UnsavedChanges extends Stimulus.Controller {
  beforeUnload(event) {
    if (this.isDirty()) {
      // Most browsers will show a default message, not our custom string :)
      event.returnValue =
        'Si vous quittez cette page sans cliquer sur le bouton Enregistrer, ' +
        'vos modifications seront perdues. ' +
        'Êtes-vous sûr·e de vouloir quitter cette page ?'
      return event.returnValue
    }
  }

  unload(event) {
    this.postStopEditing()
  }

  setDirty(event) {
    if (!this.isDirty()) {
      this.data.set('dirty', 'true')
      this.postStartEditing()
    }
  }

  allowFormSubmission(event) {
    this.data.set('dirty', 'false')
  }

  isDirty() {
    return this.data.get('dirty') === 'true'
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

  postStartEditing() {
    fetch(this.data.get('start-editing-url'), this.XHROptions())
  }

  postStopEditing() {
    fetch(this.data.get('stop-editing-url'), this.XHROptions())
  }
}

application.register('unsaved-changes', UnsavedChanges)
