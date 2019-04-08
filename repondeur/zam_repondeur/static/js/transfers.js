class Transfers extends Stimulus.Controller {
    static get targets() {
        return [
            'submitTo',
            'submitIndex',
            'amendementsWithTableActive',
            'amendementsWithTableInactive'
        ]
    }

    initialize() {
        this.verify()
    }

    check(event) {
        this.verify()
    }

    verify() {
        const hasActiveCheckedElements = this.hasCheckedElements(
            this.hasAmendementsWithTableActiveTarget
                ? this.amendementsWithTableActiveTarget
                : null
        )
        const hasInactiveCheckedElements = this.hasCheckedElements(
            this.hasAmendementsWithTableInactiveTarget
                ? this.amendementsWithTableInactiveTarget
                : null
        )
        if (hasActiveCheckedElements) {
            this.dangerClasses()
        } else if (hasInactiveCheckedElements) {
            this.warningClasses()
        } else {
            this.primaryClasses()
        }
    }

    hasCheckedElements(target) {
        if (!target) return false
        const checkboxes = Array.from(
            target.querySelectorAll('input[type="checkbox"]')
        )
        return checkboxes.some(amendement => amendement.checked)
    }

    // Sadly, Safari does not support classList.replace()
    dangerClasses() {
        this.submitToTarget.classList.add('danger')
        this.submitToTarget.classList.remove('primary')
        this.submitToTarget.classList.remove('warning')
        this.submitIndexTarget.classList.add('danger')
        this.submitIndexTarget.classList.remove('primary')
        this.submitIndexTarget.classList.remove('warning')
    }

    warningClasses() {
        this.submitToTarget.classList.add('warning')
        this.submitToTarget.classList.remove('primary')
        this.submitToTarget.classList.remove('primary')
        this.submitIndexTarget.classList.add('warning')
        this.submitIndexTarget.classList.remove('primary')
        this.submitIndexTarget.classList.remove('primary')
    }

    primaryClasses() {
        this.submitToTarget.classList.remove('warning')
        this.submitToTarget.classList.remove('danger')
        this.submitToTarget.classList.add('primary')
        this.submitIndexTarget.classList.remove('warning')
        this.submitIndexTarget.classList.remove('danger')
        this.submitIndexTarget.classList.add('primary')
    }
}
