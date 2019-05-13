class UnsavedChanges extends Stimulus.Controller {
    leaving(event) {
        if (this.isDirty()) {
            // Most browsers will show a default message, not our custom string :)
            event.returnValue =
                'Si vous quittez cette page sans cliquer sur le bouton Enregistrer, ' +
                'vos modifications seront perdues. ' +
                'Êtes-vous sûr·e de vouloir quitter cette page ?'
            return event.returnValue
        }
    }

    setDirty(event) {
        this.data.set('dirty', 'true')
    }

    allowFormSubmission(event) {
        this.data.set('dirty', 'false')
    }

    isDirty() {
        return this.data.get('dirty') === 'true'
    }
}

application.register('unsaved-changes', UnsavedChanges)
