application.register(
  'email-pattern',
  class extends Stimulus.Controller {
    delete(event) {
      if (
        window.confirm(
          'Êtes-vous sûr·e de vouloir supprimer cette adresse ? ' +
            '(cela sera effectif pour l’ensemble des dossiers)'
        )
      ) {
        return
      } else {
        event.preventDefault()
      }
    }
  }
)
