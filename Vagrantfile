# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|

  2.times do |number|
    config.vm.define "member-#{ number }" do |box|
      box.vm.box = "ubuntu/trusty64"
      box.vm.hostname = "member-#{number}"
      box.vm.network "private_network", ip: "192.168.50.1#{number}"
      box.vm.provision "ansible" do |ansible|
        ansible.playbook = "playbooks/main.yml"
      end
    end
  end
end
