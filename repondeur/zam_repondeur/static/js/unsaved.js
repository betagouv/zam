class UnsavedChanges extends Stimulus.Controller {
    formIsChanged(event) {
        this.setChanged('true')
    }

    leaving(event) {
        if (this.isFormChanged()) {
            // Most browsers will show a default message, not our custom string :)
            event.returnValue =
                'Si vous quittez cette page sans cliquer sur le bouton Enregistrer, vos modifications seront perdues. Êtes-vous sûr(e) de vouloir quitter cette page?'
            return event.returnValue
        }
    }

    allowFormSubmission(event) {
        this.setChanged('false')
    }

    setChanged(changed) {
        this.data.set('changed', changed)
    }

    isFormChanged() {
        return this.data.get('changed') == 'true'
    }
}

application.register('unsaved-changes', UnsavedChanges)
