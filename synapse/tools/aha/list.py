import sys
import asyncio
import logging
import contextlib

import synapse.exc as s_exc
import synapse.common as s_common
import synapse.telepath as s_telepath

import synapse.lib.output as s_output
import synapse.lib.version as s_version

logger = logging.getLogger(__name__)

reqver = '>=2.11.0,<3.0.0'

async def _main(argv, outp):

    async with await s_telepath.openurl(argv[0]) as prox:
        try:
            s_version.reqVersion(prox._getSynVers(), reqver)
        except s_exc.BadVersion as e:
            valu = s_version.fmtVersion(*e.get('valu'))
            outp.printf(f'Proxy version {valu} is outside of the aha supported range ({reqver}).')
            return 1
        try:
            network = argv[1]
        except IndexError:
            network = None

        mesg = f"{'Service':<20s} {'network':<30s} {'online':<6} {'scheme':<6} {'host':<20} {'port':<5}"
        outp.printf(mesg)
        async for svc in prox.getAhaSvcs(network):
            svcname = svc.get('svcname')
            svcnetw = svc.get('svcnetw')

            svcinfo = svc.get('svcinfo')
            urlinfo = svcinfo.get('urlinfo')
            online = str(bool(svcinfo.get('online')))
            host = urlinfo.get('host')
            port = str(urlinfo.get('port'))
            scheme = urlinfo.get('scheme')

            mesg = f'{svcname:<20s} {svcnetw:<30s} {online:<6} {scheme:<6} {host:<20} {port:<5} '

            outp.printf(mesg)

async def main(argv, outp=None):  # pragma: no cover

    if outp is None:
        outp = s_output.stdout

    if len(argv) not in (1, 2):
        outp.printf('usage: python -m synapse.tools.aha.list <url> [network name]')
        return 1

    s_common.setlogging(logger, 'WARNING')

    path = s_common.getSynPath('telepath.yaml')
    async with contextlib.AsyncExitStack() as ctx:

        telefini = await s_telepath.loadTeleEnv(path)
        if telefini is not None:
            ctx.push_async_callback(telefini)

        await _main(argv, outp)

    return 0

if __name__ == '__main__': # pragma: no cover
    sys.exit(asyncio.run(main(sys.argv[1:])))
