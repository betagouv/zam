Vagrant.configure("2") do |config|

  # We use Debian 10.0 (Buster) as our base image
  # cf. https://app.vagrantup.com/debian/boxes/buster64
  config.vm.box = "debian/buster64"

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
  config.hostmanager.enabled = true
  config.hostmanager.manage_host = false
  config.hostmanager.manage_guest = true

  # Configure servers using Ansible
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/site.yml"
    ansible.groups = {
      "web_servers" => ["web"],
      "app_servers" => ["app"],
      "db_servers"  => ["db"]
    }
    # ansible.limit = "all"
    ansible.become = true
    ansible.become_user = "root"
    ansible.extra_vars = {
      ansible_python_interpreter: "/usr/bin/python3",
      web_host: "web",
      web_timeout: 180,
      ssl_cert: "",
      ssl_key: "",
      app_host: "app",
      app_port: 6543,
    }
  end

end