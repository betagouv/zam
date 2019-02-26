application.register(
  'notifications',
  class extends Stimulus.Controller {
    get url() {
      return this.data.get('checkUrl')
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
        result = `<span class="${this.kind}-notification"></span> ${
          this.message
        }`
      }
      this.element.querySelector('div').innerHTML = `<p>${result}</p>`
      this.element.classList.remove('d-none')
    }

    check() {
      const options = {
        credentials: 'include'
      }
      fetch(`${this.url}?since=${this.timestamp}`, options)
        .then(reponse => reponse.json())
        .then(json => {
          if (json.modified_at && json.modified_at !== this.timestamp) {
            this.timestamp = Number(json.modified_at)
            this.message = `${this.numbersToMessage(
              json.modified_amendements_numbers,
              'amendement'
            )}`
            this.kind = 'refresh'
            this.load()
          }
        })
    }

    reset() {
      this.message = ''
      this.kind = ''
      this.element.querySelector('div').innerHTML = ''
      this.element.classList.add('d-none')
    }

    close(event) {
      event.preventDefault()
      this.reset()
    }

    fooCommaBarAndBaz(table) {
      // ['foo', 'bar', 'baz'] => 'foo, bar et baz'
      return `${table.slice(0, -1).join(', ')} et ${table.slice(-1)}`
    }

    numbersToMessage(numbers, type) {
      const length = numbers.length
      if (!length) return ''
      if (length === 1) {
        return `L’${type} ${numbers} a été mis à jour !`
      } else if (length < 10) {
        return `Les ${type}s ${this.fooCommaBarAndBaz(
          numbers
        )} ont été mis à jour !`
      } else {
        return `Les ${type}s ${numbers
          .slice(0, 4)
          .join(', ')} … ${numbers
          .slice(-4, length)
          .join(', ')} (${length} au total) ont été mis à jour !`
      }
    }
  }
)
