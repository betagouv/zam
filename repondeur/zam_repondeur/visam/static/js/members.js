application.register(
  'members',
  class extends Stimulus.Controller {
    delete(event) {
      if (
        window.confirm(
          'Êtes-vous sûr·e de vouloir retirer cette personne de ce type de conseil ? ' +
            '(il ne pourra plus accéder à aucune séance en cours ou à venir)'
        )
      ) {
        return
      } else {
        event.preventDefault()
      }
    }
  }
)
