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
      const textarea = event.target
      const initial = textarea.value.trim()

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

      // Flatten and trim emails.
      emails = emails.reduce((a, b) => a.concat(b), [])
      const result = emails.map(email => email.trim()).join('\n')

      // Deal with cursor not at the end (and potentially selected text).
      const selectedText = textarea.value.substring(
        textarea.selectionStart,
        textarea.selectionEnd
      )
      if (!selectedText) {
        textarea.value =
          textarea.value.substring(0, textarea.selectionStart) +
          '\n' +
          result +
          '\n' +
          textarea.value.substring(textarea.selectionEnd, textarea.value.length)
      } else {
        textarea.value = textarea.value.replace(selectedText, result)
      }

      // Remove remaining empty lines.
      textarea.value = textarea.value
        .split('\n')
        .filter(line => line.trim())
        .join('\n')

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
