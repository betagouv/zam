function fooCommaBarAndBaz(table) {
  // ['foo', 'bar', 'baz'] => 'foo, bar et baz'
  return `${table.slice(0, -1).join(', ')} et ${table.slice(-1)}`
}

function displayNotificationUpdate(message, kind) {
  if (kind === 'refresh') {
    message += '<a class="button primary refresh" href=>Rafraîchir</a>'
  } else {
    message = `<span class="${kind}-notification"></span> ` + message
  }
  document.querySelector('[role="status"]').innerHTML = `
    <a class="close-notification" href=>×</a><p>${message}</p>
  `
  listenToClose()
}

function amendementsNumbersToMessage(amendementsNumbers) {
  if (amendementsNumbers.length === 1) {
    return `L’amendement ${amendementsNumbers} a été mis à jour !`
  } else {
    return `Les amendements ${fooCommaBarAndBaz(
      amendementsNumbers
    )} ont été mis à jour !`
  }
}

function notifyOnUpdates(delay, timestamp, checkUrl) {
  timestamp = Number(timestamp)
  function check() {
    const options = {
      credentials: 'include'
    }
    fetch(`${checkUrl}?since=${timestamp}`, options)
      .then(reponse => reponse.json())
      .then(json => {
        if (json.modified_at && json.modified_at !== timestamp) {
          timestamp = Number(json.modified_at)
          displayNotificationUpdate(
            amendementsNumbersToMessage(json.modified_amendements_numbers),
            'refresh'
          )
        }
      })
  }
  setInterval(check, 1000 * delay)
}

function listenToClose() {
  Array.from(document.querySelectorAll('.close-notification')).forEach(closeLink => {
    closeLink.addEventListener('click', e => {
      e.preventDefault()
      document.querySelector('[role="status"]').innerHTML = ''
    })
  })
}
