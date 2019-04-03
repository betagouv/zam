class Transfers extends Stimulus.Controller {
    static get targets() {
        return ['submit', 'submitIndex', 'amendementsWithTable']
    }

    initialize() {
        this.verify()
    }

    check(event) {
        this.verify()
    }

    verify() {
        const checkboxes = Array.from(
            this.amendementsWithTableTarget.querySelectorAll(
                'input[type="checkbox"]'
            )
        )
        const hasCheckedElements = checkboxes.some(
            amendementWithTable => amendementWithTable.checked
        )
        if (hasCheckedElements) {
            this.submitTarget.classList.add('warning')
            this.submitTarget.classList.remove('primary')
            this.submitIndexTarget.classList.add('warning')
            this.submitIndexTarget.classList.remove('primary')
        } else {
            this.submitTarget.classList.remove('warning')
            this.submitTarget.classList.add('primary')
            this.submitIndexTarget.classList.remove('warning')
            this.submitIndexTarget.classList.add('primary')
        }
    }
}
