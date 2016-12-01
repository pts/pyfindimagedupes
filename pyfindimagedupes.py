#! /usr/bin/python
# by pts@fazekas.hu at Thu Dec  1 16:19:06 CET 2016

""":" #pyfindimagedupes: Finds similar duplicate images

type python2.7 >/dev/null 2>&1 && exec python2.7 -- "$0" ${1+"$@"}
type python2.6 >/dev/null 2>&1 && exec python2.6 -- "$0" ${1+"$@"}
type python2.5 >/dev/null 2>&1 && exec python2.5 -- "$0" ${1+"$@"}
type python2.4 >/dev/null 2>&1 && exec python2.4 -- "$0" ${1+"$@"}
exec python -- ${1+"$@"}; exit 1

pyfindimagedupes builds a 128-byte visual fingerprint of each specified image
file, and finds and prints images whose fingerprints are close to each other
(up to 25 1-bits in the binary xor of their fingerprints).

Usage:

  pyfindimagedupes [-n] [-v fp] [--] [<image-filename> [...]]

-n: Don't find duplicates. Useful if combined with `-v fp'.
-v fp: Print base64 fingerprint of each input image.
"""

import base64
import itertools
import os
import re
import sys

# (pip install pgmagick) or (sudo apt-get install python-pgmagick)
import pgmagick


half_threshold = (1 << (pgmagick.Image().depth() - 1)) - 1  # 127.

diff_bit_threshold = 25


def fingerprint_image(filename):
  img = pgmagick.Image(filename)
  img.sample('160x160!')
  img.modulate(100.0, -100.0, 100.0)  # saturation=-100.
  img.blur(3, 99)  # radius=3, sigma=99.
  img.normalize()
  img.equalize()
  img.sample('16x16')
  img.threshold(half_threshold)
  img.magick('mono')
  blob = pgmagick.Blob()
  img.write(blob)
  return blob.data  # 32 bytes.


def bitcount_upto8_chr(x):
  x = (x & 0x55) + ((x >> 1) & 0x55)
  x = (x & 0x33) + ((x >> 2) & 0x33)
  return chr((x & 0x0F) + ((x >> 4) & 0x0F))


bitcount8 = ''.join(bitcount_upto8_chr(x) for x in xrange(256))
bitcount_xor8 = tuple(''.join(bitcount_upto8_chr(x ^ y) for x in xrange(256))
                      for y in xrange(256))
assert ord(bitcount_xor8[123][55]) == 3


def strxor_bitcount(a, b):
  if len(a) != len(b):
    raise ValueError
  return sum(ord(bitcount_xor8[ord(ac)][ord(bc)])
             for ac, bc in itertools.izip(a, b))


assert strxor_bitcount('abxx', 'caxx') == 3


def yield_matching_groups(pairs):
  if not isinstance(pairs, (list, tuple)):
    pairs = tuple(pairs)
  if len(pairs) > 1:
    do_ignore = [False] * len(pairs)
    for i in xrange(len(pairs)):
      if not do_ignore[i]:
        matches = [
            j for j in xrange(i + 1, len(pairs)) if
            not do_ignore[j] and
            strxor_bitcount(pairs[i][1], pairs[j][1]) <= diff_bit_threshold]
        if matches:
          # All images are similar to the first file -- this doesn't mean that
          # they are similar to each other as well. We ignore them in subsequent
          # comparisons anyway.
          for j in matches:
            do_ignore[j] = True
          yield [pairs[j][0] for j in [i] + matches]


def get_module_docstring():
  return __doc__


def get_doc(doc=None):
  if doc is None:
    doc = get_module_docstring()
  doc = doc.rstrip()
  doc = re.sub(r'\A:"\s*#', '', doc, 1)
  doc = re.sub(r'\n(\ntype python.*)+\nexec python -- .*', '', doc, 1)
  return doc


def main(argv):
  if len(argv) < 2 or argv[1] == '--help':
    print get_doc()
    sys.exit(0)
  try:
    is_n = False
    is_vfp = False
    i = 1
    while i < len(argv):
      arg = argv[i]
      i += 1
      if arg == '--':
        break
      if not arg.startswith('-') or arg == '-':
        i -= 1
        break
      if arg == '-v':
        if i < len(argv) and argv[i] == 'fp':
          is_vfp = True
          i += 1
        else:
          raise ValueError('Expected fp after -v.')
      elif arg == '-n':
        is_n = True
      else:
        raise ValueError('Unknown flag: %s' % arg)
  except ValueError, e:
    print >>sys.stderr, 'error: %s\n\n%s\n\nerror: %s' % (e, get_doc(), e)
    sys.exit(1)

  # Calling abspath for compatibility with the findimagedupes Perl script.
  filenames = map(os.path.abspath, argv[i:])
  # TODO(pts): Catch and handle RuntimeError on fingerprint_image.
  if is_vfp or not is_n:
    pairs = []
    for filename in filenames:
      fp = fingerprint_image(filename)
      if is_vfp:
        sys.stdout.write('%s  %s\n' % (base64.b64encode(fp), filename))
        sys.stdout.flush()
      if not is_n:
        pairs.append((filename, fp))
    for matching_filenames in yield_matching_groups(pairs):
      print ' '.join(matching_filenames)


if __name__ == '__main__':
  sys.exit(main(sys.argv))
