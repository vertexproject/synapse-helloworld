import os
import hellostormsvc
import synapse.tests.utils as s_test

class HelloTest(s_test.SynTest):

    async def test_hello_basics(self):

        async with self.getTestCore() as core:

            path = os.path.join(core.dirn, 'hello')

            async with await hellostormsvc.HelloWorldCell.anit(path) as hello:
                svcurl = hello.getLocalUrl()

                # add the service to the test cortex
                opts = {'vars': {'svcurl': svcurl}}
                await core.stormlist('service.add hello $svcurl', opts=opts)

                # ensure the service gets a connected
                await core.callStorm('$lib.service.wait(hello)')

                # test the hello.lookup command
                nodes = await core.nodes('[ inet:fqdn=vertex.link ] | hello.lookup --yield')
                self.len(2, nodes)
                ndefs = [ node.ndef for node in nodes ]
                self.eq((
                    ('inet:dns:a', ('vertex.link', 0x01020304)),
                    ('inet:dns:a', ('vertex.link', 0x05060708)),
                ), ndefs)

                # test hello debug output
                msgs = await core.stormlist('[ inet:fqdn=vertex.link ] | hello.lookup --debug')
                self.stormIsInPrint('hello.lookup resolving: vertex.link', msgs)

                # test the hello.stream command
                nodes = await core.nodes('[ inet:fqdn=vertex.link ] | hello.stream')
                self.len(2, nodes)
                ndefs = [ node.ndef for node in nodes ]
                self.eq((
                    ('inet:dns:a', ('vertex.link', 0x01010101)),
                    ('inet:dns:a', ('vertex.link', 0x02020202)),
                ), ndefs)
