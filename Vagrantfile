Vagrant.configure("2") do |config|

  config.vm.box = "fedora/34-cloud-base"
  config.vm.synced_folder ".", "/vagrant", type: "virtualbox"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = 2048
  end

  config.vm.network(
    "forwarded_port", guest: 8000, host: 8000, host_ip: "127.0.0.1"
  )
  
  config.vm.provision "shell", path: "bootstrap.sh", privileged: false

end
