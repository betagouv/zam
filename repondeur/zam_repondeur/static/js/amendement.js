class Amendement extends Stimulus.Controller {
  static get targets() {
    return ['avis', 'reponse']
  }
  checkEmptyAvis(event) {
    // TinyMCE is generating an iframe for each handled textarea,
    // we cannot access it easily from (Stimulus)JS.
    const reponseValue = this.reponseTarget.parentElement.querySelector(
      'iframe#reponse_ifr.tox-edit-area__iframe'
    ).contentWindow.document.body.textContent
    if (this.avisTarget.value === '' && reponseValue !== '') {
      const accept = confirm(
        'Vous vous apprêtez à sauvegarder une réponse sans avis'
      )
      if (!accept) event.preventDefault()
    }
  }
}
