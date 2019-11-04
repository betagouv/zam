application.register(
  'progress',
  class extends Stimulus.Controller {
    get url() {
      const url = new URL(this.data.get('checkUrl'), window.location)
      return url.pathname
    }

    initialize() {
      this.initial = this.element.innerHTML
      if (this.url) {
        setInterval(() => {
          this.check()
        }, 1000 * this.data.get('checkInterval'))
      }
    }

    check() {
      const headers = new Headers({
        'X-Requested-With': 'XMLHttpRequest'
      })
      const options = {
        credentials: 'include',
        headers: headers
      }
      fetch(this.url, options)
        .then(reponse => reponse.json())
        .then(this.formatReponse.bind(this))
        .catch(console.error.bind(console))
    }

    formatReponse(progress) {
      const isEmpty = Object.entries(progress).length === 0
      const isComplete = !isEmpty && progress.current === progress.total
      const inProgress = this.element.innerText.startsWith(
        'Récupération en cours'
      )
      if (isEmpty || isComplete) {
        this.restore()
        if (inProgress) {
          this.updateTimestamp()
        }
        return
      }
      const percents = Math.round(progress.current / progress.total * 100)
      this.element.innerHTML = `
        Récupération en cours : ${percents}%<br>
        <progress value="${progress.current}" max="${
        progress.total
      }"></progress>
      `
    }

    restore() {
      this.element.innerHTML = this.initial
    }

    updateTimestamp() {
      const timeElement = this.element.querySelector('time')
      timeElement.dataset.timestampModifiedAt = Date.now()
      const refreshButton =
        ' <a class="button primary enabled" href=".">Actualiser&nbsp;?</a>'
      if (!this.initial.endsWith(refreshButton)) {
        this.element.insertAdjacentHTML('beforeend', refreshButton)
        this.initial = this.element.innerHTML
      }
    }
  }
)
