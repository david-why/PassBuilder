# PassBuilder: Make Apple Wallet passes for yourself

PassBuilder is a Siri Shortcut that lets you create custom Apple Wallet passes.

## Structure

This project has two parts:

- [api](api): This folder contains the backend of the project, written in JavaScript and deployed to Cloudflare Workers. It is responsible for signing the pass that is created by a shortcut.
- [shortcut](shortcut): This folder contains the `PassBuilder` shortcut which is used to create passes. You should install the signed [PassBuilder.shortcut](https://github.com/david-why/PassBuilder/raw/refs/heads/main/shortcut/PassBuilder.shortcut); the unsigned [PassBuilder.unsigned.shortcut](shortcut/PassBuilder.unsigned.shortcut) is included for diffs. The Python files are an attempt to write the shortcut with [WorkflowPy](https://github.com/david-why/workflowpy) which failed.

## Usage

1. Install [the shortcut](https://github.com/david-why/PassBuilder/raw/refs/heads/main/shortcut/PassBuilder.shortcut). This can't be executed directly; you need to create your own shortcut to use it.
2. Create a new shortcut, and put the following actions:
   1. Text: Put the JSON content of your pass here. The format is described later.
   2. Run Shortcut: Choose the `PassBuilder` shortcut you installed earlier, and set the input to the Text variable from the first action.
   3. Save File: Save the pass you created to a file. (On iOS, the saved file can't be opened directly. See below for a workaround.)
3. Run the shortcut to create the pass.

## JSON Content Format

The JSON content is an object of the following form:

```ts
interface Content {
    pass: Pass;
    images: Record<string, string>;
    name?: string;
}
```

The `Pass` type is the format of the "pass.json" file [as described by Apple here](https://developer.apple.com/documentation/walletpasses/pass). If you need help creating the content of a pass, check out [this official guide from Apple](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html).

The `images` object contains a mapping of image file names to their Base64 content. These files will be placed in the pass with the filename being the key and the content being the Base64 decoded value.

The `name` value is only used for naming the returned file. If provided, the returned pass file name will be `` `${name}.pkpass` ``. Otherwise, the file name will be `"pass.pkpass"`. It does not have any effect on the contents of the file.

## Workaround for iOS devices

On iOS devices, when you attempt to open a saved `.pkpass` file in the Files app, you will be greeted with the default preview and cannot import the pass. If you intend to run the shortcut on iOS devices, I suggest that you use the following list of actions for your shortcut:

1. Text: Same as above.
2. Run Shortcut: Same as above.
3. Base64 Encode: Set the mode to "Encode" and the input to the result variable of Run Shortcut. Make sure to set "Line breaks" to "None".
4. Open URLs: Set the URL to the following: `data:application/vnd.apple.pkpass;base64,[Base64 Encoded]`. `[Base64 Encoded]` is the variable from the Base64 Encode action.

This will convert the pass into a data URL and open this in Safari, which will bring up a prompt to import the pass.
