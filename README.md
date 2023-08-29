# EDeA Measurement Server

edea-ms provides an API and user interface for planning, executing and analyzing measurement data for electronics engineering purposes. It allows engineering teams or collaborating individuals to automate tests and share results in a unified way, be it for board bringup, silicon evaluation or other test and measurement tasks.

This project is based on the original EDeA Project proposal and takes further inspiration from the [TestOps Manifesto by Keysight](https://www.keysight.com/us/en/assets/7018-06546/white-papers/5992-3771.pdf).

## Current Status

We're using and developing this at Fully Automated for our OSHW and consulting projects. It's in a usable state, but currently only used internally. If you intend to use this, please contact us so we can understand the usecase of other engineering teams better.

## Running it

As we haven't released an official release yet, building and running it still requires a few dependencies like poetry and npm. With those installed it's just two commands:

```sh
# run the server
poetry run uvicorn app.main:app --reload

# run the frontend
npm run dev
```

## Measurement Client

See the [EDeA TMC](https://gitlab.com/edea-dev/edea-tmc) project for a library with which one can write test programs with.

## Licenses

The server code is licensed under the [EUPL-1.2 license](LICENSE.txt) and the frontend code is licensed under the [MIT license](LICENSE.frontend.txt).
Images and artwork are licensed under CC BY-ND 4.0.

Linking the server code (e.g. using it as a library) is allowed under the EUPL-1.2, even for commercial use. Modifications should be shared but the server code is structured in a way that it can easily be integrated in other systems (internal or otherwise) without modifying the core.

If you want to host a modified frontend internally or externally, please replace the logos so that it's clear that it is a modified distribution.
