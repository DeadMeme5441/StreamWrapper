#!/usr/bin/env python3
import ffmpeg
import json


def test():
    """
    Testing script, use only for temp testing of input and output.
    """
    server_udp = "udp://192.168.0.108:5000?pkt_size=1316"
    server_https = "http://127.0.0.1:8080"

    audio = ffmpeg.input("hw:0", f="alsa")
    video = ffmpeg.input("/dev/video0", input_format="h264")

    process = (
        ffmpeg.concat(video, audio, v=1, a=1)
        .output(
            server_https,
            listen=1,
            pix_fmt="yuvj420p",
            level=4.1,
            preset="ultrafast",
            tune="zerolatency",
            vcodec="libx264",
            video_bitrate=512000,
            threads=2,
            acodec="aac",
            f="mpegts",
            r=10,
            s="640x480",
            flush_packets=0,
        )
        .run()
    )


def read_config(config_file_path="./config.json"):
    """
    Reads the default config of the server and sends it as a dictionary.
    All config settings are saved in the config.json file in the same directory.
    If it returns an empty dict, please run write_config function to generate the config first.
    DO NOT directly edit the config.json unless you're fully certain of the ffmpeg options and
    also the ffmpeg-python library syntax.
    """
    conf = {}

    with open(config_file_path, "r") as config_file:
        conf = json.load(config_file)

    return conf[0]


def write_config():
    """
    Global config writer, edit the entire config file with no issues.
    Backup stored as backup_config.json
    Confirms changes in the end so you can always re-write.
    """
    config = {}
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    with open("backup_config.json", "w") as def_config_file:
        json.dump(config, def_config_file)

    config = config[0]

    new_config = edit_dict(config)
    confirm = input("Would you like to save your new config?(Y/N)")

    if confirm in ("Y", "y"):
        with open("config.json", "w") as config_file:
            json.dump(config, config_file)
        print("Config has been changed. Older config saved as backup_config.json")

    elif confirm in ("N", "n"):
        print("Changes not saved, config file is untouched.")


def edit_dict(inp_dict):
    """
    Recursive dict writer, made just to edit config json.
    """

    for key in inp_dict:

        if type(inp_dict[key]) == dict:
            print("The setting for " + key + " contains the following options : ")
            for nkey in inp_dict[key]:
                print(nkey)
            choice = input("Would you like to enter " + str(key) + " property?\n")

        else:
            choice = input("Would you like to edit " + str(key) + " ?\n")

        if choice in ("Y", "y") and type(inp_dict[key]) != dict:
            if inp_dict[key] != "":
                print("Current Value = " + inp_dict[key])
            changed_val = input("Enter value for field : " + key + "\n")
            inp_dict[key] = changed_val

        elif choice in ("Y", "y") and type(inp_dict[key]) == dict:
            edit_dict(inp_dict[key])

        elif choice in ("N", "n"):
            continue

    return inp_dict


def gen_server_string(protocol, protocol_dict):
    """
    Generates input server string based on protocol.
    If it returns an empty string, please check the config file if the settings have been udpated.
    """

    input_server = ""

    if protocol == "rtsp":
        input_server = (
            "rtsp://"
            + protocol_dict["hostname"]
            + ":"
            + protocol_dict["port"]
            + "/"
            + protocol_dict["path"]
        )
    elif protocol == "rtp":
        input_server = (
            "rtp://"
            + protocol_dict["hostname"]
            + ":"
            + protocol_dict["port"]
            + "/"
            + protocol_dict["options"]
        )
    elif protocol == "rtmp":
        input_server = (
            "rtmp://"
            + protocol_dict["username"]
            + ":"
            + protocol_dict["password"]
            + "@"
            + protocol_dict["server"]
            + ":"
            + protocol_dict["port"]
            + "/"
            + protocol_dict["app"]
            + "/"
            + protocol_dict["instance"]
            + "/"
            + protocol_dict["path"]
        )
    elif protocol == "mpeg-ts":
        input_server = (
            "udp://"
            + protocol_dict["hostname"]
            + ":"
            + protocol_dict["port"]
            + protocol_dict["options"]
        )
    elif protocol == "srt":
        input_server = (
            "srt://" + protocol_dict["hostname"] + ":" + protocol_dict["port"]
        )
    elif protocol == "hls":
        input_server = (
            "hls+http://" + protocol_dict["host"] + "/" + protocol_dict["path"]
        )

    return input_server


def gen_settings():
    """
    Generates final settings for the stream to start, from the config file.
    """
    config = read_config()
    final_settings = {}

    in_protocol = ""
    in_protocol_dict = {}

    for key in config["input_stream"]["protocols"]:
        if config["input_stream"]["protocols"][key]["enabled"] is True:
            in_protocol = str(key)
            in_protocol_dict = config["input_stream"]["protocols"][key]

    out_protocol = ""
    out_protocol_dict = {}

    for key in config["output_stream"]["protocols"]:
        if config["output_stream"]["protocols"][key]["enabled"] is True:
            out_protocol = str(key)
            out_protocol_dict = config["output_stream"]["protocols"][key]

    in_video_codec = ""
    for key in config["input_stream"]["codecs"]["video_codecs"]:
        if config["input_stream"]["codecs"]["video_codecs"][key]["enabled"] is True:
            in_video_codec = config["input_stream"]["codecs"]["video_codecs"][key][
                "value"
            ]

    in_audio_codec = ""
    for key in config["input_stream"]["codecs"]["audio_codecs"]:
        if config["input_stream"]["codecs"]["audio_codecs"][key]["enabled"] is True:
            in_audio_codec = config["input_stream"]["codecs"]["audio_codecs"][key][
                "value"
            ]

    out_video_codec = ""
    for key in config["output_stream"]["codecs"]["video_codecs"]:
        if config["output_stream"]["codecs"]["video_codecs"][key]["enabled"] is True:
            out_video_codec = config["output_stream"]["codecs"]["video_codecs"][key][
                "value"
            ]

    out_audio_codec = ""
    for key in config["output_stream"]["codecs"]["audio_codecs"]:
        if config["output_stream"]["codecs"]["audio_codecs"][key]["enabled"] is True:
            out_audio_codec = config["output_stream"]["codecs"]["audio_codecs"][key][
                "value"
            ]

    final_settings["input_server"] = gen_server_string(in_protocol, in_protocol_dict)
    final_settings["output_server"] = gen_server_string(out_protocol, out_protocol_dict)
    final_settings["input_video_codec"] = in_video_codec
    final_settings["input_audio_codec"] = in_audio_codec
    final_settings["output_video_codec"] = out_video_codec
    final_settings["output_audio_codec"] = out_audio_codec
    final_settings["additional_settings"] = config["additional_settings"]

    return final_settings


def start_server(final_setts):
    """
    Starts server with final settings passed as a parameter.
    """

    process = (
        ffmpeg.input(final_setts["input_server"], listen=1)
        .output(
            final_setts["output_server"],
            vcodec=final_setts["output_video_codec"],
            acodec=final_setts["output_audio_codec"],
            **final_setts["additional_settings"],
        )
        .run()
    )


def stop_server():

    return_code = 1
    return return_code


def get_server_meta():

    metadata = {}
    return metadata


if __name__ == "__main__":

    print("Pulling config for streaming wrapper.")
    fin_settings = gen_settings()
    print(fin_settings)
    start_server(fin_settings)
