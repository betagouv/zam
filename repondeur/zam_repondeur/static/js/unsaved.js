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
    this.data.set('dirty', 'true')
    this.postStartEditing()
  }

  allowFormSubmission(event) {
    this.data.set('dirty', 'false')
  }

  isDirty() {
    return this.data.get('dirty') === 'true'
  }

  postStartEditing() {
    fetch(this.data.get('start-editing-url'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
  }

  postStopEditing() {
    fetch(this.data.get('stop-editing-url'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
  }
}

application.register('unsaved-changes', UnsavedChanges)
