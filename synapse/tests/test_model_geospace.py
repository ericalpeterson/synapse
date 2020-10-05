import synapse.exc as s_exc
import synapse.common as s_common

import synapse.tests.utils as s_t_utils
from synapse.tests.utils import alist

import synapse.lib.module as s_module

geotestmodel = {

    'ctors': (),

    'types': (
        ('test:latlong', ('geo:latlong', {}), {}),
        ('test:distoff', ('geo:dist', {'baseoff': 1000}), {}),
    ),

    'forms': (

        ('test:latlong', {}, (
            ('lat', ('geo:latitude', {}), {}),
            ('long', ('geo:longitude', {}), {}),
            ('dist', ('geo:dist', {}), {}),
        )),
        ('test:distoff', {}, ()),
    ),
}

geojson0 = {
    "type": "GeometryCollection",
    "bbox": [-110, -45, 110, 45],
    "geometries": [
        {
            "type": "Point",
            "coordinates": [0, 0]
        },
        {
            "type": "LineString",
            "coordinates": [[-110, 45], [110, -45]]
        },
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [100.0, 0.0],
                    [101.0, 0.0],
                    [101.0, 1.0],
                    [100.0, 1.0],
                    [100.0, 0.0]
                ],
                [
                    [100.8, 0.8],
                    [100.8, 0.2],
                    [100.2, 0.2],
                    [100.2, 0.8],
                    [100.8, 0.8]
                ]
            ]
        }
    ]
}

geojson1 = {
    "type": "MultiPolygon",
    "coordinates": [
        [
            [
                [102.0, 2.0, 10],
                [103.0, 2.0, 10],
                [103.0, 3.0, 10],
                [102.0, 3.0, 10],
                [102.0, 2.0, 10]
            ]
        ],
        [
            [
                [100.0, 0.0, 20],
                [101.0, 0.0, 20],
                [101.0, 1.0, 20],
                [100.0, 1.0, 20],
                [100.0, 0.0, 20]
            ],
            [
                [100.2, 0.2, 30],
                [100.8, 0.2, 30],
                [100.8, 0.8, 30],
                [100.2, 0.8, 30],
                [100.2, 0.2, 30]
            ]
        ]
    ]
}

geojson2 = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": "1",
            "geometry": {
                "type": "Point",
                "coordinates": [0, 0]
            },
            "properties": {
                "name": "basic"
            }
        }
    ]
}

badcopnodonut = {
    "type": "GeometryCollection",
    "geometries": [
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [100.0, 0.0],
                    [101.0, 0.0],
                    [101.0, 1.0],
                    [100.0, 1.0]
                ]
            ]
        }
    ]
}

worscopnodonut = {
    "type": "GeometryCollection",
    "geometries": [
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [100.0, 0.0],
                    [101.0, 0.0],
                    [101.0, 1.0],
                    [102.0, 1.0],
                    [102.0, 2.0],
                    [102.0, 1.0],
                    [101.0, 1.0],
                    [100.0, 1.0],
                    [100.0, 0.0]
                ]
            ]
        }
    ]
}


class GeoTstModule(s_module.CoreModule):
    def getModelDefs(self):
        return (
            ('geo:test', geotestmodel),
        )

class GeoTest(s_t_utils.SynTest):

    async def test_types_forms(self):
        formlat = 'geo:latitude'
        formlon = 'geo:longitude'
        formlatlon = 'geo:latlong'

        async with self.getTestCore() as core:
            # Latitude Type Tests =====================================================================================
            t = core.model.type(formlat)
            self.raises(s_exc.BadTypeValu, t.norm, '-90.1')
            self.eq(t.norm('-90')[0], -90.0)
            self.eq(t.norm('-12.345678901234567890')[0], -12.34567890123456789)
            self.eq(t.norm('-0')[0], 0.0)
            self.eq(t.norm('0')[0], 0.0)
            self.eq(t.norm('12.345678901234567890')[0], 12.34567890123456789)
            self.eq(t.norm('90')[0], 90.0)
            self.eq(t.norm('39.94891608')[0], 39.94891608)
            self.raises(s_exc.BadTypeValu, t.norm, '90.1')
            self.raises(s_exc.BadTypeValu, t.norm, 'newp')

            # Longitude Type Tests =====================================================================================
            t = core.model.type(formlon)
            self.raises(s_exc.BadTypeValu, t.norm, '-180.0')
            self.eq(t.norm('-12.345678901234567890')[0], -12.34567890123456789)
            self.eq(t.norm('-0')[0], 0.0)
            self.eq(t.norm('0')[0], 0.0)
            self.eq(t.norm('12.345678901234567890')[0], 12.34567890123456789)
            self.eq(t.norm('180')[0], 180.0)
            self.eq(t.norm('39.94891608')[0], 39.94891608)
            self.raises(s_exc.BadTypeValu, t.norm, '180.1')
            self.raises(s_exc.BadTypeValu, t.norm, 'newp')

            # Latlong Type Tests =====================================================================================
            t = core.model.type(formlatlon)
            self.eq(t.norm('0,-0'), ((0.0, 0.0), {'subs': {'lat': 0.0, 'lon': 0.0}}))
            self.eq(t.norm('89.999,179.999'), ((89.999, 179.999), {'subs': {'lat': 89.999, 'lon': 179.999}}))
            self.eq(t.norm('-89.999,-179.999'), ((-89.999, -179.999), {'subs': {'lat': -89.999, 'lon': -179.999}}))

            self.eq(t.norm([89.999, 179.999]), ((89.999, 179.999), {'subs': {'lat': 89.999, 'lon': 179.999}}))
            self.eq(t.norm((89.999, 179.999)), ((89.999, 179.999), {'subs': {'lat': 89.999, 'lon': 179.999}}))

            # Demonstrate precision
            self.eq(t.norm('12.345678,-12.345678'),
                    ((12.345678, -12.345678), {'subs': {'lat': 12.345678, 'lon': -12.345678}}))
            self.eq(t.norm('12.3456789,-12.3456789'),
                    ((12.3456789, -12.3456789), {'subs': {'lat': 12.3456789, 'lon': -12.3456789}}))
            self.eq(t.norm('12.34567890,-12.34567890'),
                    ((12.3456789, -12.3456789), {'subs': {'lat': 12.3456789, 'lon': -12.3456789}}))

            self.eq(t.repr((0, 0)), '0,0')
            self.eq(t.repr((0, -0)), '0,0')
            self.eq(t.repr((12.345678, -12.345678)), '12.345678,-12.345678')

            # Geo-dist tests
            formname = 'geo:dist'
            t = core.model.type(formname)

            self.eq(t.norm('100km')[0], 100000000)
            self.eq(t.norm('100     km')[0], 100000000)
            self.eq(t.norm('837.33 m')[0], 837330)
            self.eq(t.norm('11.2 km'), (11200000, {}))
            self.eq(t.norm(11200000), (11200000, {}))

            self.eq(t.repr(5), '5 mm')
            self.eq(t.repr(500), '50.0 cm')
            self.eq(t.repr(1000), '1.0 m')
            self.eq(t.repr(10000), '10.0 m')
            self.eq(t.repr(1000000), '1.0 km')

            self.raises(s_exc.BadTypeValu, t.norm, '1.3 pc')
            self.raises(s_exc.BadTypeValu, t.norm, 'foo')

            # geo:nloc
            formname = 'geo:nloc'
            t = core.model.type(formname)

            ndef = ('inet:ipv4', '0.0.0.0')
            latlong = ('0.000000000', '0')
            stamp = -0

            place = s_common.guid()
            props = {'place': place,
                     'loc': 'us.hehe.haha'}

            async with await core.snap() as snap:
                node = await snap.addNode('geo:nloc', (ndef, latlong, stamp), props=props)
                self.eq(node.ndef[1], (('inet:ipv4', 0), (0.0, 0.0), stamp))
                self.eq(node.get('ndef'), ('inet:ipv4', 0))
                self.eq(node.get('ndef:form'), 'inet:ipv4')
                self.eq(node.get('latlong'), (0.0, 0.0))
                self.eq(node.get('time'), 0)
                self.eq(node.get('place'), place)
                self.eq(node.get('loc'), 'us.hehe.haha')
                self.nn(await snap.getNodeByNdef(('inet:ipv4', 0)))

            # geo:place

            # test inline tuple/float with negative syntax...
            node = (await alist(core.eval('[ geo:place="*" :latlong=(-30.0,20.22) ]')))[0]
            self.eq(node.get('latlong'), (-30.0, 20.22))

            async with await core.snap() as snap:
                guid = s_common.guid()
                parent = s_common.guid()
                props = {'name': 'Vertex  HQ',
                         'desc': 'The place where Vertex Project hangs out at!',
                         'address': '208 Datong Road, Pudong District, Shanghai, China',
                         'parent': parent,
                         'loc': 'us.hehe.haha',
                         'latlong': '34.1341, -118.3215',
                         'bbox': '2.11, 2.12, -4.88, -4.9',
                         'radius': '1.337km'}
                node = await snap.addNode('geo:place', guid, props)
                self.eq(node.ndef[1], guid)
                self.eq(node.get('name'), 'vertex hq')
                self.eq(node.get('loc'), 'us.hehe.haha')
                self.eq(node.get('latlong'), (34.1341, -118.3215))
                self.eq(node.get('radius'), 1337000)
                self.eq(node.get('desc'), 'The place where Vertex Project hangs out at!')
                self.eq(node.get('address'), '208 datong road, pudong district, shanghai, china')
                self.eq(node.get('parent'), parent)

                self.eq(node.get('bbox'), (2.11, 2.12, -4.88, -4.9))
                self.eq(node.repr('bbox'), '2.11,2.12,-4.88,-4.9')

                opts = {'vars': {'place': parent}}
                nodes = await core.nodes('geo:place=$place', opts=opts)
                self.len(1, nodes)

            q = '[geo:place=(beep,) :latlong=$latlong]'
            opts = {'vars': {'latlong': (11.38, 20.01)}}
            nodes = await core.nodes(q, opts)
            self.len(1, nodes)
            self.eq(nodes[0].get('latlong'), (11.38, 20.01))

    async def test_eq(self):

        async with self.getTestCore() as core:
            async with await core.snap() as snap:

                guid0 = s_common.guid()
                props = {'name': 'Vertex  HQ',
                         'latlong': '34.1341, -118.3215',
                         'radius': '1.337km'}
                node = await snap.addNode('geo:place', guid0, props)
                self.nn(node)

                guid1 = s_common.guid()
                props = {'name': 'Griffith Observatory',
                         'latlong': '34.1341, -118.3215',
                         'radius': '75m'}
                node = await snap.addNode('geo:place', guid1, props)
                self.nn(node)

            nodes = await core.nodes('geo:place:latlong=(34.1341, -118.3215)')
            self.len(2, nodes)

            nodes = await core.nodes('geo:place:latlong=(34.1341, -118.3)')
            self.len(0, nodes)

            nodes = await core.nodes('geo:place:latlong=(34.1, -118.3215)')
            self.len(0, nodes)

    async def test_near(self):

        async with self.getTestCore() as core:
            async with await core.snap() as snap:
                # These two nodes are 2,605m apart
                guid0 = s_common.guid()
                props = {'name': 'Vertex  HQ',
                         'latlong': '34.1341, -118.3215',  # hollywood sign
                         'radius': '1.337km'}
                node = await snap.addNode('geo:place', guid0, props)
                self.nn(node)

                guid1 = s_common.guid()
                props = {'name': 'Griffith Observatory',
                         'latlong': '34.118560, -118.300370',
                         'radius': '75m'}
                node = await snap.addNode('geo:place', guid1, props)
                self.nn(node)

                guid2 = s_common.guid()
                props = {'name': 'unknown location'}
                node = await snap.addNode('geo:place', guid2, props)
                self.nn(node)

                # A telemetry node for example by the observatory
                guid3 = s_common.guid()
                props = {'latlong': '34.118660, -118.300470'}
                node = await snap.addNode('tel:mob:telem', guid3, props)
                self.nn(node)

                # A telemetry node for example by the HQ
                guid4 = s_common.guid()
                props = {'latlong': '34.13412, -118.32153'}
                node = await snap.addNode('tel:mob:telem', guid4, props)
                self.nn(node)

                # Far away nodes to test bounding box
                guid5 = s_common.guid()
                props = {'latlong': '35.118660, -118.300470'}
                node = await snap.addNode('tel:mob:telem', guid5, props)
                self.nn(node)

                guid6 = s_common.guid()
                props = {'latlong': '33.118660, -118.300470'}
                node = await snap.addNode('tel:mob:telem', guid6, props)
                self.nn(node)

            # Node filtering behavior
            nodes = await core.nodes('geo:place +:latlong*near=((34.1, -118.3), 10km)')
            self.len(2, nodes)
            nodes = await core.nodes('geo:place +geo:place:latlong*near=((34.1, -118.3), 10km)')
            self.len(2, nodes)

            nodes = await core.nodes('geo:place +:latlong*near=((34.1, -118.3), 50m)')
            self.len(0, nodes)

            # +1's come from the unknown loc without a latlong prop
            nodes = await core.nodes('geo:place -:latlong*near=((34.1, -118.3), 10km)')
            self.len(0 + 1, nodes)
            nodes = await core.nodes('geo:place -:latlong*near=((34.1, -118.3), 50m)')
            self.len(2 + 1, nodes)

            # Storm variable use to filter nodes based on a given location.
            q = f'geo:place={guid0} $latlong=:latlong $radius=:radius | spin | geo:place +:latlong*near=($latlong, ' \
                f'$radius)'
            nodes = await alist(core.eval(q))
            self.len(1, nodes)

            q = f'geo:place={guid0} $latlong=:latlong $radius=:radius | spin | geo:place +:latlong*near=($latlong, 5km)'
            nodes = await alist(core.eval(q))
            self.len(2, nodes)

            # Lifting nodes by *near=((latlong), radius)
            nodes = await alist(core.eval('geo:place:latlong*near=((34.1, -118.3), 10km)'))
            self.len(2, nodes)

            nodes = await alist(core.eval('geo:place:latlong*near=(("34.118560", "-118.300370"), 50m)'))
            self.len(1, nodes)

            nodes = await alist(core.eval('geo:place:latlong*near=((0, 0), 50m)'))
            self.len(0, nodes)

            # Use a radius to lift nodes which will be inside the bounding box,
            # but outside the cmpr implemented using haversine filtering.
            nodes = await alist(core.eval('geo:place:latlong*near=(("34.118560", "-118.300370"), 2600m)'))
            self.len(1, nodes)

            # Storm variable use to lift nodes based on a given location.
            q = f'geo:place={guid1} $latlong=:latlong $radius=:radius ' \
                f'tel:mob:telem:latlong*near=($latlong, 3km) +tel:mob:telem'
            nodes = await alist(core.eval(q))
            self.len(2, nodes)

            q = f'geo:place={guid1} $latlong=:latlong $radius=:radius ' \
                f'tel:mob:telem:latlong*near=($latlong, $radius) +tel:mob:telem'
            nodes = await alist(core.eval(q))
            self.len(1, nodes)

        async with self.getTestCore() as core:
            await core.loadCoreModule('synapse.tests.test_model_geospace.GeoTstModule')
            # Lift behavior for a node whose has a latlong as their primary property
            nodes = await core.nodes('[(test:latlong=(10, 10) :dist=10m) '
                                     '(test:latlong=(10.1, 10.1) :dist=20m) '
                                     '(test:latlong=(3, 3) :dist=5m)]')
            self.len(3, nodes)

            nodes = await core.nodes('test:latlong*near=((10, 10), 5km)')
            self.len(1, nodes)
            nodes = await core.nodes('test:latlong*near=((10, 10), 30km)')
            self.len(2, nodes)

            # Ensure geo:dist inherits from IntBase correctly
            nodes = await core.nodes('test:latlong +:dist>5m')
            self.len(2, nodes)
            nodes = await core.nodes('test:latlong +:dist>=5m')
            self.len(3, nodes)
            nodes = await core.nodes('test:latlong +:dist<5m')
            self.len(0, nodes)
            nodes = await core.nodes('test:latlong +:dist<=5m')
            self.len(1, nodes)
            nodes = await core.nodes('test:latlong:dist>5m')
            self.len(2, nodes)
            nodes = await core.nodes('test:latlong:dist>=5m')
            self.len(3, nodes)
            nodes = await core.nodes('test:latlong:dist<5m')
            self.len(0, nodes)
            nodes = await core.nodes('test:latlong:dist<=5m')
            self.len(1, nodes)

            nodes = await core.nodes('test:latlong +:dist*range=(8m, 10m)')
            self.len(1, nodes)
            nodes = await core.nodes('test:latlong:dist*range=(8m, 10m)')
            self.len(1, nodes)

    async def test_geojson(self):

        async with self.getTestCore() as core:

            with self.raises(s_exc.BadTypeValu):
                opts = {'vars': {'geojson': {}}}
                nodes = await core.nodes('[ geo:place=* :geojson=$geojson ]', opts=opts)

            opts = {'vars': {'geojson': geojson0}}
            nodes = await core.nodes('[ geo:place=* :geojson=$geojson ]', opts=opts)

            opts = {'vars': {'geojson': geojson1}}
            nodes = await core.nodes('[ geo:place=* :geojson=$geojson ]', opts=opts)

            opts = {'vars': {'geojson': geojson2}}
            nodes = await core.nodes('[ geo:place=* :geojson=$geojson ]', opts=opts)

            opts = {'vars': {'geojson': badcopnodonut}}
            nodes = await core.nodes('[ geo:place=* :geojson=$geojson ]', opts=opts)
            opts = {'vars': {'geojson': worscopnodonut}}
            nodes = await core.nodes('[ geo:place=* :geojson=$geojson ]', opts=opts)

    def test_shapely(self):
        # depending on your version, use: from shapely.geometry import shape, Point

        # load GeoJSON file containing sectors
        # with open('sectors.json') as f:
        #     js = json.load(f)
        #
        # # construct point based on lon/lat returned by geocoder
        # point = Point(-122.7924463, 45.4519896)
        #
        # # check each polygon to see if it contains the point
        # for feature in js['features']:
        #     polygon = shape(feature['geometry'])
        #     if polygon.contains(point):
        #         print
        #         'Found containing polygon:', feature
        import json
        import shapely.geometry as sgm
        import geojson

        points = (
            (-122.7924463, 45.4519896),
            (100, 0.3),
        )

        # for feature in geojson0.get(''):
        #     pass

        obj = geojson.loads(json.dumps(geojson0))
        print(obj)
        print(type(obj))

        def getPolygons(obj):
            '''Yield polygons out of a geojson struct'''
            otyp = obj.get('type')
            if otyp == 'FeatureCollection':
                features = obj.get('features')
                for feat in features:
                    yield from getPolygons(feat)
            elif otyp == 'Feature':
                geometry = obj.get('geometry')
                if geometry is None:
                    return
                yield from getPolygons(geometry)
                # geotype = geometry.get('type')
                # if geotype == 'Polygon':
                #     yield geometry.get('coordinates')
                # # TODO support other polys?
            elif otyp == 'GeometryCollection':
                geometry = obj.get('geometries')
                for geo in geometry:
                    yield from getPolygons(geo)
            elif otyp == 'Polygon':
                coords = obj.get('coordinates')
                yield coords
            elif otyp == 'MultiPolygon':
                coords_list = obj.get('coordinates')
                for coords in coords_list:
                    yield coords

        blob = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [102.0, 0.5]
                },
                "properties": {
                    "prop0": "value0"
                }
            },
                {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [102.0, 0.0],
                        [103.0, 1.0],
                        [104.0, 0.0],
                        [105.0, 1.0]
                    ]
                },
                "properties": {
                    "prop0": "value0",
                    "prop1": 0.0
                }
            }, {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [100.0, 0.0],
                            [101.0, 0.0],
                            [101.0, 1.0],
                            [100.0, 1.0],
                            [100.0, 0.0]
                        ]
                    ]
                },
                "properties": {
                    "prop0": "value0",
                    "prop1": {
                        "this": "that"
                    }
                }
            }]
        }

        obj = geojson.loads(json.dumps(blob))
        print(obj)
        print(obj.is_valid)
        print(type(obj))

        for k, v in obj.items():
            print(k)
            print(v)

        print('--------------------------------')
        obj = geojson.loads(json.dumps(badcopnodonut))
        print(obj)
        print(obj.is_valid)
        print(obj.errors())
        print(type(obj))
        print(list(obj))
        print(dir(obj))

        print('--------------------------------')
        obj = geojson.loads(json.dumps(worscopnodonut))
        print(obj)
        print(obj.is_valid)
        print(obj.errors())

        print(20 * '*%*')

        for poly in getPolygons(blob):
            print(poly)
            print('ooo')
            shape = sgm.polygon.Polygon()

        for poly in getPolygons(geojson2):
            print(poly)
            print('ooo')

        thing = sgm.mapping(geojson.loads(json.dumps(blob)))
        print(thing)
        print(dir(thing))

        thing = sgm.mapping(geojson.loads(json.dumps(worscopnodonut)))
        print(thing)
        print(dir(thing))

        print('polly check')
        tps = []

        for poly in getPolygons(geojson0):
            shell = poly
            holes = None
            if len(poly) > 1:
                shell = poly[0]
                holes = poly[1:]
            polygony = sgm.Polygon(shell=shell, holes=holes)
            print(polygony)
            for point in (
                [100.1, 0.1, ],
                [100.1, 0.2],
                [100, 3.0],
            ):
                p = sgm.Point(*point)
                print(p)
                print(polygony.contains(p))

        print('fin -!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1')

    async def test_geo_dist_offset(self):

        async with self.getTestCore() as core:

            await core.loadCoreModule('synapse.tests.test_model_geospace.GeoTstModule')
            nodes = await core.nodes('[ test:distoff=-3cm ]')
            self.eq(970, nodes[0].ndef[1])
            self.eq('-3.0 cm', await core.callStorm('test:distoff return($node.repr())'))
            with self.raises(s_exc.BadTypeValu):
                nodes = await core.nodes('[ test:distoff=-3km ]')
