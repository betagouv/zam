application.register('table-menu', class extends Stimulus.Controller {
    toggle(event) {
        event.preventDefault()
        this.element.classList.toggle('open')
    }
})

application.register('table-anchor', class extends Stimulus.Controller {
    initialize() {
        if (location.hash) {
            /* Waiting for the next tick to supplement previous browser behavior. */
            setTimeout(() => {
                const element = document.querySelector(window.location.hash)
                const target = element.getBoundingClientRect()
                window.scrollTo({
                    /* Position the highlighted element in the middle of the page. */
                    top: window.scrollY + target.top - window.innerHeight / 2 + target.height / 2,
                    behavior: 'smooth'
                })
            }, 1)
        }
    }
})
