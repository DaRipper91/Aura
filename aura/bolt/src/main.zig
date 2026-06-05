const std = @import("std");
const ollama = @import("ollama.zig");

pub fn main(init: std.process.Init) !void {
    const allocator = init.arena.allocator();

    const args = try init.minimal.args.toSlice(allocator);

    if (args.len < 3) {
        std.debug.print("Usage: {s} <model> <prompt>\n", .{args[0]});
        return;
    }

    const model = args[1];
    const prompt = args[2];

    var client = ollama.OllamaClient.init(allocator, "http://localhost:11434", init.io);
    try client.streamChat(model, prompt);
}
