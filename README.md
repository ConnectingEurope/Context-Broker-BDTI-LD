# CBLD-BDTI

**Please note that support questions will not be monitored during the summer period of July and August. **

> **NOTICE**: For this version, the solution provider made every effort to provide a stable and functional release. 
> No thorough testing was conducted due to the absence of a Cygnus Linked Data ready version. 
> There is warranty, expressed or implied, as to the reliability and stability of the solution. 
> The support team remains available to help on any issue that can be encountered and any feedback is thoroughly appreciated.

CEF Context Broker Linked Data integration with the Big Data Test Infrastructure.

This Integration Solution connects a Orion CB-LD with a Cygnus,
allowing the user to easily configure the storing of the context data in
BDTIs file system (HDFS). The application:

- Manages CBs subscriptions to Cygnus (create and delete)
- Sets how and where the context data will be stored
- Automatically deploys Cygnus each time a change done in its
  configuration is done

All this information is provided by a configuration file that
establishes the parametrics to do so.

CBLD-BDTI core component ([`cbld_bdti/`](src/cbld_bdti/)) is a command line
interface application (CLI) that offers the commands and options needed
to work with the integration.

## Getting Started

The following instructions will allow you to get a completely functional
CBLD-BDTI environment. This is just a guideline about how to install and
deploy the solution. Adapt it to your needs.

### Prerequisites

CBLD-BDTI has some requirements that should be accomplished before
starting deploying it.

- Ubuntu 18.04.1 LTS 64-bit or later
- Python 3.6 or later
- pip3 9.0.1 or later

Update packages list in case you didn't do before (recommended):

```commandline
sudo apt update
```

#### Python 3.7 installation

Python 3 is already installed in Ubuntu 18 distributions. However, in
case you want to use Python 3.7, follow the next steps to install it.

First update packages list and install the prerequisites:

```commandline
sudo apt install software-properties-common
```

Then add the deadsnakes PPA to your sources list:

```commandline
sudo add-apt-repository ppa:deadsnakes/ppa
```

Last, install Python 3.7 with:

```commandline
sudo apt install python3.7
```

You can verify if everything is alright just typing (it should print
Python version number):

```commandline
$ python3.7 --version
Python 3.7.3
```

#### pip3 installation

pip3 will be used as the package manager for Python. It will be used for
CB-EDP installation, so must be installed before starting the
deployment.

After packages list update, install pip for Python 3:

```commandline
sudo apt install python3-pip
```

You can verify the installation typing:

```commandline
$ pip3 --version
pip 9.0.1 from /usr/lib/python3/dist-packages (python 3.7)
```

### Installing and deploying

#### CBLD-BDTI core component

To install the Integration Solution, download this repository as a ZIP
file and move it to the machine where you want to deploy it. Once you
got it, install it using pip:

```commandline
sudo pip3 install /path/to/cb_bdti.zip
```

It should have installed too every dependency (Click, configobj and
paramiko) of the CBLD-BDTI. In case it didn't or you aren't sure of it,
install them directly using [`requirements.txt`](requirements.txt) file.
First unzip it cause it's on downloaded ZIP file:

```commandline
unzip /path/to/cbld_bdti.zip
pip3 install -r /path/to/requirements.txt
```

You can check it's installed launching `show` pip3 command:

```commandline
$ pip3 show cbld-bdti
---
Metadata-Version: 1.0
Name: cbld-bdti
Version: 0.1
Summary: FIWARE Context Broker Linked Data instance integration with the BDTI
Home-page: https://github.com/ConnectingEurope/Context-Broker-BDTI-LD
Location: /usr/local/lib/python3.7/dist-packages
Requires: Click, configobj, paramiko, requests
Classifiers:
Entry-points:
  [console_scripts]
  cbld-bdti=cbld_bdti.commands:cli
```

### SSH tunneling to HDFS cluster

Connecting to BDTI could be difficult because of its security measures.
You will need to make a tunnel between Cygnus server and BDTI HDFS in
order to allow Cygnus to persist context data. In the following steps
this process will be explained just as a tutorial or guidelines that can
help you to get a working communication between these applications.
Adapt it to your needs.

First of all:

- You will need a key file to HDFS server. This should be provided by
  BDTI team and it will be used to made the tunnel possible.
- Copy hostname of every Data Nodes on the cluster. You can do this
  executing:

    ```commandline
    sudo -uhdfs hdfs dfsadmin -report
    ```

Now you need to install [autossh](https://www.harding.motd.ca/autossh/)
in Cygnus machine. Update packages list in case you didn't do before and
install it:

```commandline
sudo apt-get update
sudo apt-get install autossh
```

Once it's installed, create the tunnel for Name Node from Cygnus machine
replacing the values:

- `{bastion_private_key}` for the path of Bastion machine private key
- `{namenode_port}` for the NameNode WebUI port (50070 by default)
- `{hostname_namenode}` for the hostname of Name Node cluster
- `{bastion_username}` for the username of Bastion machine
- `{bastion_host}` for the host of Bastion machine

```commandline
autossh -i {bastion_private_key} -N -L {namenode_port}:{hostname_namenode}:{namenode_port} {bastion_username}@{bastion_host}
```

Then, create the tunnels for the Data Nodes from Cygnus machine
executing the command for each Data Node you have and replacing the
values:

- `{bastion_private_key}` for the path of Bastion machine private key
- `{namenode_port}` for the NameNode WebUI port (50070 by default)
- `{hostname_namenode}` for the hostname of Name Node cluster
- `{bastion_username}` for the username of Bastion machine
- `{bastion_host}` for the host of Bastion machine

```commandline
autossh -i {bastion_private_key} -N –L {datanode_port}:{hostname_datanode}:{datanode_port} {bastion_username}@{bastion_host}
```

At last, add for each Data Node the next line in `{/etc/hosts}` file in
Cygnus machine replacing:

- `{host_datanode}` for the hostname of each Data Node of the cluster

```text
127.0.0.1 {host_datanode} localhost
```

You can test WebHDFS connection doing a `curl` to `localhost` on `50070`
port for Name Node (by default) or `50075` port for Data Node (by
default).

## Built With

- [Python 3.7](https://www.python.org/)

## License

This project is licensed under the European Union Public License 1.2
-see the [LICENSE](LICENSE) file for details.

## Contributors

The Context Broker - Big Data Test Infrastructure enabler (NGSI-LD) has been carried out by:

- [CEF Digital](https://ec.europa.eu/cefdigital/wiki/display/CEFDIGITAL/CEF+Digital+Home)
- [everis](https://www.everis.com/)
- [FIWARE](https://www.fiware.org/)
