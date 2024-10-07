def annotate_lines(infile: str, outfile: str, annotation: dict[int, str]):
    line_number = 1
    with open(infile) as inf:
        with open(outfile, "w") as outf:
            for line in inf:
                line = line.rstrip()
                ann = annotation.get(line_number, None)
                if ann is not None:
                    print(f"{line.rstrip()} # {ann}", file=outf)
                else:
                    print(line, file=outf)

                line_number += 1
