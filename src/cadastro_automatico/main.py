import argparse

from cadastro_automatico.robot import Robot


def main():
    parser = argparse.ArgumentParser(
        description="Automação de cadastro de funcionários no OrangeHRM."
    )

    parser.add_argument(
        "-idt",
        required=True,
        help="Identificador desta execução.",
    )

    arguments = parser.parse_args()
    print("""
        ██████╗  ███╗   ██╗              ██████╗ ███████╗██╗   ██╗
        ██╔════╝ ████╗  ██║              ██╔══██╗██╔════╝██║   ██║
        ██║  ███╗██╔██╗ ██║    █████╗    ██║  ██║█████╗  ██║   ██║
        ██║   ██║██║╚██╗██║    ╚════╝    ██║  ██║██╔══╝  ╚██╗ ██╔╝
        ╚██████╔╝██║ ╚████║              ██████╔╝███████╗ ╚████╔╝
        ╚═════╝ ╚═╝  ╚═══╝              ╚═════╝ ╚══════╝  ╚═══╝
          """)

    robot = Robot()
    robot.start(arguments)


if __name__ == "__main__":
    main()