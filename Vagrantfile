Vagrant.configure("2") do |config|
  config.vm.box = "fedora/34-cloud-base"
  config.vm.synced_folder ".", "/vagrant", type: "virtualbox"
    config.vm.provider "virtualbox" do |vb|
	vb.memory = 2048
  end
end
