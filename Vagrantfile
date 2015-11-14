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
      box.vm.provision "shell", inline: <<SCRIPT
wget -O- -o/dev/null http://www.rabbitmq.com/rabbitmq-signing-key-public.asc | apt-key add - \
&& echo 'deb http://www.rabbitmq.com/debian/ testing main' > /etc/apt/sources.list.d/rabbitmq.list \
&& apt-get update -yyq \
&& apt-get install -yyq rabbitmq-server \
&& rabbitmq-plugins enable rabbitmq_shovel \
&& rabbitmq-plugins enable rabbitmq_federation \
&& rabbitmq-plugins enable rabbitmq_federation_management \
&& rabbitmq-plugins enable rabbitmq_shovel_management \
&& service rabbitmq-server restart \
&& curl -s http://localhost:15672/cli/rabbitmqadmin > /usr/local/bin/rabbitmqadmin \
&& chmod +x /usr/local/bin/rabbitmqadmin \
&& curl -s https://raw.githubusercontent.com/ModusCreateOrg/slow/master/slow > /usr/local/bin/slow \
&& chmod +x /usr/local/bin/slow
SCRIPT
    end
  end
end
