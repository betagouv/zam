class Notifications extends Stimulus.Controller {
  get url() {
    const url = new URL(this.data.get('checkUrl'), window.location)
    const params = url.searchParams
    params.set('since', this.timestamp)
    return `${url.pathname}?${params.toString()}`
  }

  get message() {
    return this.data.get('message')
  }

  set message(value) {
    return this.data.set('message', value)
  }

  get kind() {
    return this.data.get('kind')
  }

  set kind(value) {
    return this.data.set('kind', value)
  }

  get timestamp() {
    return Number(this.data.get('checkTimestamp'))
  }

  set timestamp(value) {
    return this.data.set('checkTimestamp', value)
  }

  initialize() {
    if (this.message) this.load()
    if (this.url && this.timestamp) {
      setInterval(() => {
        this.check()
      }, 1000 * this.data.get('checkInterval'))
    }
  }

  load() {
    if (!this.message) return
    let result
    if (this.kind === 'refresh') {
      result = `${
        this.message
      } <a class="button primary refresh" href=>Rafraîchir</a>`
    } else {
      result = `<span class="${this.kind}-notification"></span> ${this.message}`
    }
    this.element.querySelector('div').innerHTML = `<p>${result}</p>`
    this.element.classList.replace('d-none', `notification-${this.kind}`)
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

  formatReponse(json) {
    if (json.modified_at && json.modified_at !== this.timestamp) {
      this.timestamp = Number(json.modified_at)
      this.message = this.numbersToMessage(json.modified_amendements_numbers)
      this.kind = 'refresh'
      this.load()
    }
  }

  reset() {
    this.element.classList.replace(`notification-${this.kind}`, 'd-none')
    this.message = ''
    this.kind = ''
    this.element.querySelector('div').innerHTML = ''
  }

  close(event) {
    event.preventDefault()
    this.reset()
  }

  fooCommaBarAndBaz(table) {
    // ['foo', 'bar', 'baz'] => 'foo, bar et baz'
    return `${table.slice(0, -1).join(', ')} et ${table.slice(-1)}`
  }

  numbersToMessage(numbers) {
    if (!numbers) return ''
    const length = numbers.length
    if (!length) return ''
    if (length === 1) {
      return `L’amendement ${numbers} a été mis à jour !`
    } else if (length < 10) {
      return `Les amendements ${this.fooCommaBarAndBaz(
        numbers
      )} ont été mis à jour !`
    } else {
      return `Les amendements ${numbers
        .slice(0, 4)
        .join(', ')} … ${numbers
        .slice(-4, length)
        .join(', ')} (${length.toLocaleString('fr')} au total) ont été mis à jour !`
    }
  }
}

class NotificationsWithDiff extends Notifications {
  get kind() {
    return 'refresh'
  }

  get url() {
    const url = new URL(this.data.get('checkUrl'), window.location)
    const params = url.searchParams
    params.set('current', this.current)
    return `${url.pathname}?${params.toString()}`
  }

  get current() {
    return this.data.get('current')
  }

  set current(value) {
    return this.data.set('current', value)
  }

  initialize() {
    if (this.url) {
      setInterval(() => {
        this.check()
      }, 1000 * this.data.get('checkInterval'))
    }
  }

  formatReponse(json) {
    if ('updated' in json) {
      this.message = this.numbersToMessage(json.updated.split('_'))
      this.load()
    }
  }

  numbersToMessage(numbers) {
    const initial = this.current.split('_')
    const [added, removed] = this.getAddedorRemovedItems(initial, numbers)
    let message = ''
    const addedLength = added.length
    if (addedLength && added[0] !== '') {
      if (addedLength === 1) {
        message += `L’amendement ${added[0]} a été ajouté à votre table. `
      } else {
        message += `Les amendements ${this.fooCommaBarAndBaz(
          added
        )} ont été ajoutés à votre table. `
      }
    }
    const removedLength = removed.length
    if (removedLength && removed[0] !== '') {
      if (removedLength === 1) {
        message += `L’amendement ${removed[0]} a été retiré de votre table.`
      } else {
        message += `Les amendements ${this.fooCommaBarAndBaz(
          removed
        )} ont été retirés de votre table.`
      }
    }
    return message
  }

  getAddedorRemovedItems(initial, compared) {
    return [
      compared.filter(item => initial.indexOf(item) === -1),
      initial.filter(item => compared.indexOf(item) === -1)
    ]
  }
}

class NotificationsWithDiffUnique extends NotificationsWithDiff {
  get kind() {
    return 'danger'
  }

  numbersToMessage(numbers) {
    const initial = this.current.split('_')
    const [added, removed] = this.getAddedorRemovedItems(initial, numbers)
    const num = this.data.get('amendementNum')
    if (!removed.includes(num)) return ''
    document
      .querySelectorAll('.save-buttons input[type="submit"]')
      .forEach(input => input.classList.add('disabled'))
    return `L’amendement en cours d’édition n’est plus sur votre table.
      Votre saisie ne va PAS être sauvegardée.
      <a class="button primary enabled" href="${this.data.get(
        'tableUrl'
      )}">Retourner à ma table</a>`
  }
}

application.register('notifications', Notifications)
