import sys
import asyncio
import synapse.lib.cell as s_cell
import synapse.lib.stormsvc as s_stormsvc

# each service needs a unique id
svciden = '457a11723f821dd8884cb5f9d80596ad'
svcconf = {'svciden': svciden}

class HelloWorldService(s_stormsvc.StormSvc, s_cell.CellApi):
    '''
    HelloWorldService implements an example Storm Service.
    '''
    _storm_svc_name = 'helloworld'
    _storm_svc_vers = (1, 0, 0)
    _storm_svc_pkgs = (
        {
            'name': 'hello',
            'version': (1, 0, 0),
            'svcconf': svcconf,
            'modules': (
                {
                    'name': 'hello',
                    'modconf': svcconf,
                    'storm': '''
                        function lookup(fqdn) {

                            $retn = $lib.list()

                            $hellosvc = $lib.service.get($modconf.svciden)

                            $answ = $hellosvc.runDnsLook($fqdn)

                            for $ipv4 in $answ.ipv4s {
                                [ inet:dns:a=($fqdn, $ipv4)]
                                $retn.append($node)
                            }

                            fini{ return($retn) }
                        }
                    '''
                },
            ),
            'commands': (
                {
                    'name': 'hello.lookup',
                    'descr': 'Lookup an FQDN in the helloworld example service.',
                    'cmdargs': (
                        # -h / --help plumbing happens automatically
                        ('--yield', {'default': False, 'action': 'store_true',
                            'help': 'Yield created inet:dns:a nodes instead of the inbound inet:fqdn nodes.'}),
                        ('--debug', {'default': False, 'action': 'store_true',
                            'help': 'Print detailed user feedback.'}),
                    ),
                    'cmdconf': {'svciden': svciden},
                    'storm': '''
                        // Filter out all node types other than inet:fqdn
                        +inet:fqdn

                        $fqdn = $node.repr()

                        if $cmdopts.debug {
                            $lib.print("hello.lookup resolving: {fqdn}", fqdn=$fqdn)
                        }

                        // import our hello module
                        $hello = $lib.import(hello)
                        $nodes = $hello.lookup($fqdn)

                        if $cmdopts.yield {
                            -> { yield $nodes }
                        }
                    ''',
                },
                {
                    'name': 'hello.stream',
                    'descr': 'Yield a potentially large number of results from a service.',
                    'cmdargs': (),
                    'cmdconf': {'svciden': svciden},
                    'storm': '''
                        // Filter out all node types other than inet:fqdn
                        +inet:fqdn

                        $hellosvc = $lib.service.get($cmdconf.svciden)

                        $fqdn = $node.repr()
                        -> {
                            for $ipv4 in $hellosvc.runGenrLook($fqdn) {
                                [ inet:dns:a = ($fqdn, $ipv4) ]
                            }
                        }
                    ''',
                },
            ),
        },
    )

    async def runDnsLook(self, fqdn):
        # pretend to run a DNS lookup and return results
        # ( but in reality you could do anything and return it here )
        return {'ipv4s': [ '1.2.3.4', '5.6.7.8' ] }

    async def runGenrLook(self, fqdn):
        # storm services may also expose python generators
        # to allow streaming results of any size without memory pressure
        yield '1.1.1.1'
        yield '2.2.2.2'

class HelloWorldCell(s_cell.Cell):
    '''
    A Cell stores persistant information such as users and permissions.
    '''
    cellapi = HelloWorldService

if __name__ == '__main__':
    asyncio.run(HelloWorldCell.execmain(sys.argv[1:]))
