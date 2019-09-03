application.register(
  'dossier-item',
  class extends Stimulus.Controller {
    delete(event) {
      if (
        window.confirm(
          'Êtes-vous sûr·e de vouloir supprimer toutes les données ' +
            'relatives à ce dossier (lectures, avis et réponses) ?'
        )
      ) {
        return
      } else {
        event.preventDefault()
      }
    }
  }
)

application.register(
  'dossier-invite',
  class extends Stimulus.Controller {
    clean(event) {
      /* https://stackoverflow.com/a/52078216 */
      const reg = /[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/g
      const paste = (event.clipboardData || window.clipboardData).getData(
        'text'
      )
      const separators = [';', ',', '\n']
      let emails = []
      separators.forEach(separator => {
        if (paste.includes(separator)) {
          emails = paste.split(separator).map(line => line && line.match(reg))
        }
      })
      if (!emails.length) {
        emails = [paste]
      }
      event.target.value = emails.join('\n')
      event.preventDefault()
    }
  }
)

application.register(
  'dossier-retrait',
  class extends Stimulus.Controller {
    delete(event) {
      if (
        window.confirm(
          'Êtes-vous sûr·e de vouloir retirer cette personne du dossier ? '
        )
      ) {
        return
      } else {
        event.preventDefault()
      }
    }
  }
)

