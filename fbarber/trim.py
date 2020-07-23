'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from fbarber import seqio
import regex
from typing import Pattern, Match, Optional, Tuple


class FastxExtractor(object):
    """Trimming class for fasta and fastq files"""

    __matched_count: int = 0
    __unmatched_count: int = 0

    def __init__(self, pattern: Pattern, fmt: str,
                 flag_delim: str = "¦", comment_space: str = " "):
        super(FastxExtractor, self).__init__()
        self._pattern = pattern
        assert fmt in ["fasta", "fastq"]
        self.__fmt = fmt
        assert 1 == len(flag_delim)
        self.__delim = flag_delim
        assert 1 == len(comment_space)
        self.__comment_space = comment_space
        if "fasta" == self.__fmt:
            self.extract = self._extract_fasta
        elif "fastq" == self.__fmt:
            self.extract = self._extract_fastq

    @property
    def matched_count(self):
        return self.__matched_count

    @property
    def unmatched_count(self):
        return self.__unmatched_count

    @property
    def parsed_count(self):
        return self.__matched_count + self.__unmatched_count

    def extract(self, record: seqio.FastxSimpleRecord
                ) -> Tuple[seqio.FastxSimpleRecord, bool]:
        pass

    def _extract_fastq(self, record: seqio.FastqSimpleRecord
                       ) -> Tuple[seqio.FastqSimpleRecord, bool]:
        name, seq, qual = record
        match = regex.match(self._pattern, seq)
        if match is None:
            self.__unmatched_count += 1
            return (record, False)
        else:
            seq = regex.sub(self._pattern, "", seq)
            name = self.__update_name(name, match, qual)
            qual = qual[-len(seq):]
            self.__matched_count += 1
            return ((name, seq, qual), True)

    def _extract_fasta(self, record: seqio.FastaSimpleRecord
                       ) -> Tuple[seqio.FastaSimpleRecord, bool]:
        name, seq = record
        match = regex.match(self._pattern, seq)
        if match is None:
            self.__unmatched_count += 1
            return (record, False)
        else:
            seq = regex.sub(self._pattern, "", seq)
            name = self.__update_name(name, match)
            self.__matched_count += 1
            return ((name, seq), True)

    def __update_name(self, name: str, match: Match,
                      qual: Optional[str] = None) -> str:
        name_bits = name.split(self.__comment_space)
        for label, value in match.groupdict().items():
            name_bits[0] += f"{self.__delim}{self.__delim}{label}"
            name_bits[0] += f"{self.__delim}{value}"
        name = " ".join(name_bits)
        if qual is not None:
            qual_bits = ""
            flags = list(match.groupdict().keys())
            for gid in range(len(match.groups())):
                group_name = flags[gid]
                group_qual = qual[match.start(gid + 1):match.end(gid + 1)]
                qual_bits += f"{self.__delim}{self.__delim}q{group_name}"
                qual_bits += f"{self.__delim}{group_qual}"
            name += qual_bits
        return name