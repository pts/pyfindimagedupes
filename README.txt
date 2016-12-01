pyfindimagedupes: Finds similar duplicate images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pyfindimagedupes is a command-line Python script which builds a 128-byte
visual fingerprint of each specified image file, and finds and prints images
whose fingerprints are close to each other (up to 25 1-bits in the binary
xor of their fingerprints). pyfindimagedups is a compatible (and a bit slow)
reference reimplementation of a subset of the findimagedupes Perl script.
The base64 fingerprint outputs should be identical.

pyfindimagedupes needs Python 2.4, 2.5, 2.6 or 2.7 (no Python 3.x) and
pgmagick installed.

The command-line syntax is compatible with the findimagedupes Perl script's.
By default, it computes fingerprints in memory for each input file, then
compares fingerprints and prints file groups.

Significant differences from the findimagedups Perl script:

* pyfindimagedupes doesn't deduplicate filenames.
* pyfindimagedupes emits filenames within a group in a deterministic order.
* pyfindimagedupes doesn't have recovery from image file errors.

The findimagedupes Perl script is documented here:
http://manpages.ubuntu.com/manpages/precise/man1/findimagedupes.1p.html

The findimagedups Go program (https://github.com/opennota/findimagedupes) is
unrelated. It also uses a different fingerprint algorithm and output.

__END__
