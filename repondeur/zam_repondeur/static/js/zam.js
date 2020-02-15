application.register(
  'timestamp',
  class extends Stimulus.Controller {
    initialize() {
      this.epochs = [
        ['année', 31536000],
        ['mois', 2592000],
        ['jour', 86400],
        ['heure', 3600],
        ['minute', 60],
        ['seconde', 1]
      ]
      const modifiedAt = this.data.get('modifiedAt')
      const date = this.timestampToDate(modifiedAt)
      this.element.textContent = this.timeAgo(date)
    }

    timestampToDate(timestamp) {
      return new Date(timestamp * 1000)
    }

    timeAgo(date) {
      const getDuration = timeAgoInSeconds => {
        for (let [name, seconds] of this.epochs) {
          const interval = Math.floor(timeAgoInSeconds / seconds)

          if (interval >= 1) {
            return {
              interval: interval,
              epoch: name
            }
          }
        }
        return {
          interval: 0,
          epoch: 'now'
        }
      }
      const timeAgoInSeconds = Math.floor((new Date() - date) / 1000)
      const { interval, epoch } = getDuration(timeAgoInSeconds)
      if (epoch === 'now') {
        return `à lʼinstant`
      } else {
        const suffix = interval === 1 || epoch === 'mois' ? '' : 's'
        return `il y a ${interval} ${epoch}${suffix}`
      }
    }
  }
)

application.register(
  'menu',
  class extends Stimulus.Controller {
    static get targets() {
      return ['menu']
    }
    toggle(event) {
      event.preventDefault()
      this.menuTarget.classList.toggle('d-none')
    }
    dismiss(event) {
      if (!this.element.contains(event.target)) {
        this.menuTarget.classList.toggle('d-none', true)
      }
    }
  }
)

application.register(
  'amendement-search',
  class extends Stimulus.Controller {
    static get targets() {
      return ['link', 'form', 'input', 'error']
    }

    open(event) {
      event.preventDefault()
      this.formTarget.classList.toggle('d-none')
    }

    submit(event) {
      event.preventDefault()
      const value = this.inputTarget.value
      const urlSearchAmendement = this.formTarget.dataset.urlSearchAmendement
      const url = new URL(urlSearchAmendement)
      url.search = `num=${value}`
      fetch(url)
        .then(response => response.json())
        .then(urls => {
          window.location = urls['index']
        })
        .catch(e => this.errorTarget.classList.remove('d-none'))
    }

    reset(event) {
      this.errorTarget.classList.add('d-none')
    }
  }
)
