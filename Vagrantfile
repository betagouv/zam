Vagrant.configure("2") do |config|

  # We use CentOS 7 as our base image
  # cf. https://app.vagrantup.com/centos/boxes/7
  config.vm.box = "centos/7"

  # Front-end web server
  config.vm.define :web do |web|
    web.vm.network "private_network", ip: "192.168.10.33"
    web.vm.hostname = "web"

    # Forward some ports to the host
    # cf. https://www.vagrantup.com/docs/networking/forwarded_ports.html
    web.vm.network "forwarded_port", guest: 80, host: 9080
    web.vm.network "forwarded_port", guest: 443, host: 9443
  end

  # Application server
  config.vm.define :app do |app|
    app.vm.network "private_network", ip: "192.168.10.34"
    app.vm.hostname = "app"
  end

  # Database server
  config.vm.define :db do |db|
    db.vm.network "private_network", ip: "192.168.10.35"
    db.vm.hostname = "db"
  end

  # Automatically update /etc/hosts file when servers are brought up/down
  # (requires the vagrant-hostmanager plugin)
  # config.hostmanager.enabled = true
  # config.hostmanager.manage_host = false
  # config.hostmanager.manage_guest = true

end