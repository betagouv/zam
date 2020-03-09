class FormRequired extends Stimulus.Controller {
  check(event) {
    // TinyMCE is generating an iframe for each handled textarea,
    // we cannot access it easily from (Stimulus)JS and the `required`
    // attribute is not effective by default. Here we iterate through these
    // elements and manually check the content of the iframe to alert
    // the user about the required field.
    // Half-full glass: the message is more relevant than browser's defaults.
    const requiredElements = this.element.querySelectorAll('textarea[required]')
    Array.from(requiredElements).forEach(requiredElement => {
      const name = requiredElement.name
      const label = this.element.querySelector(`label[for="${name}"]`)
      const iframe = this.element.querySelector(
        `iframe#${name}_ifr.tox-edit-area__iframe`
      )
      const content = iframe.contentWindow.document.body.textContent
      if (content === '') {
        alert(`Le champ « ${label.textContent} » est requis.`)
        event.preventDefault()
      }
    })
  }
}
application.register('form-required', FormRequired)
