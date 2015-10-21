from fanstatic import Library, Resource, init_needed, bundle_resources, sort_resources
from fanstatic import Inclusion

from fanstatic.core import Bundle


def test_bundle_resources():
    foo = Library('foo', '')
    x1 = Resource(foo, 'a.css')
    x2 = Resource(foo, 'b.css')
    x3 = Resource(foo, 'c.css', dont_bundle=True)

    bar = Library('bar', '')
    y1 = Resource(bar, 'y1.css')
    y2 = Resource(bar, 'y2.css')
    y3 = Resource(bar, 'subdir/y3.css')
    y4 = Resource(bar, 'subdir/y4.css')
    init_needed()

    bundle = bundle_resources([x1, x2])
    assert len(bundle) == 1
    assert isinstance(bundle[0], Bundle)

    # x3 is not bundle safe.
    bundle = bundle_resources([x1, x3])
    assert len(bundle) == 2
    # We don't create bundles of one element.
    assert bundle[0] == x1
    assert bundle[1] == x3

    # x2 and x1 are not bundled because x3 is in the way.
    # (sort_resources in NeededResources fixes the sorting)
    bundle = bundle_resources([x1, x3, x2])
    assert bundle == [x1, x3, x2]

    # The resources are sorted by renderer order, library dependencies
    # and resource dependencies.
    bundle = bundle_resources(sort_resources([x1, x3, x2]))
    assert len(bundle) == 2
    assert isinstance(bundle[0], Bundle)
    assert bundle[1] == x3

    bundle = bundle_resources([x1, x2, y1, y2])
    assert len(bundle) == 2

    bundle = bundle_resources([y1, y2, y3, y4])
    assert len(bundle) == 2


def test_render_bundle():
    foo = Library('foo', '')
    x1 = Resource(foo, 'a.css')
    x2 = Resource(foo, 'b.css')
    x3 = Resource(foo, 'c.css', dont_bundle=True)
    x4 = Resource(foo, 'subdir/subdir/x4.css')
    x5 = Resource(foo, 'subdir/subdir/x5.css')
    needed = init_needed(resources=[x1, x2, x3])
    incl = Inclusion(needed)
    assert incl.render() == '''<link rel="stylesheet" type="text/css" href="/fanstatic/foo/a.css" />
<link rel="stylesheet" type="text/css" href="/fanstatic/foo/b.css" />
<link rel="stylesheet" type="text/css" href="/fanstatic/foo/c.css" />'''

    needed = init_needed(resources=[x1, x2, x3])
    incl = Inclusion(needed, bundle=True)
    assert incl.render() == '''<link rel="stylesheet" type="text/css" href="/fanstatic/foo/:bundle:a.css;b.css" />
<link rel="stylesheet" type="text/css" href="/fanstatic/foo/c.css" />'''

    needed = init_needed(resources=[x1, x2, x4, x5])
    incl = Inclusion(needed, bundle=True)
    assert incl.render() == '''<link rel="stylesheet" type="text/css" href="/fanstatic/foo/:bundle:a.css;b.css" />
<link rel="stylesheet" type="text/css" href="/fanstatic/foo/subdir/subdir/:bundle:x4.css;x5.css" />'''

