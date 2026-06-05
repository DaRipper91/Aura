const std = @import("std");

pub const OllamaClient = struct {
    allocator: std.mem.Allocator,
    base_url: []const u8,
    io: std.Io,

    pub fn init(allocator: std.mem.Allocator, base_url: []const u8, io: std.Io) OllamaClient {
        return .{
            .allocator = allocator,
            .base_url = base_url,
            .io = io,
        };
    }

    pub fn streamChat(self: *OllamaClient, model: []const u8, prompt: []const u8) !void {
        var client = std.http.Client{ 
            .allocator = self.allocator,
            .io = self.io,
        };
        defer client.deinit();

        const endpoint = try std.fmt.allocPrint(self.allocator, "{s}/api/generate", .{self.base_url});
        defer self.allocator.free(endpoint);
        const uri = try std.Uri.parse(endpoint);

        const payload = try std.fmt.allocPrint(self.allocator, 
            \\{{
            \\  "model": "{s}",
            \\  "prompt": "{s}",
            \\  "stream": true
            \\}}
        , .{ model, prompt });
        defer self.allocator.free(payload);

        var req = try client.request(.POST, uri, .{
            .extra_headers = &[_]std.http.Header{
                .{ .name = "Content-Type", .value = "application/json" },
            },
        });
        defer req.deinit();

        try req.sendBodyComplete(payload);

        var redirect_buffer: [1024]u8 = undefined;
        var response = try req.receiveHead(&redirect_buffer);

        var body_buffer: [4096]u8 = undefined;
        var body_reader = response.reader(&body_buffer);
        
        var stdout_buffer: [1024]u8 = undefined;
        var stdout_file_writer: std.Io.File.Writer = .init(.stdout(), self.io, &stdout_buffer);
        const stdout_writer = &stdout_file_writer.interface;

        var buffer: [1024]u8 = undefined;
        while (true) {
            const bytes_read = try body_reader.readSliceShort(&buffer);
            if (bytes_read == 0) break;
            
            try stdout_writer.writeAll(buffer[0..bytes_read]);
            try stdout_writer.flush();
        }
    }
};
