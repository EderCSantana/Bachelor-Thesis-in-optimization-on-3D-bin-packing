         Vert.append(new_lines[2][5])
            Hori.append(new_lines[2][3])
            Dep.append(new_lines[2][1])
            print("Dep:", Dep)
            print("Hori:", Hori)
            print("Vert:", Vert)
            cut_group = [Dep, Vert, Hori]
            print(cut_group)
            cut_draws(file_name, cut_group)