// Loaded by the QuantConnect LEAN Launcher with local, read-only research data.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.Json;
using QuantConnect.Data;

namespace QuantConnect.Algorithm.CSharp
{
    public class ResearchReplay : QCAlgorithm
    {
        private const decimal Initial = 100_000_000m;
        private readonly Dictionary<string, Account> _accounts = new()
        {
            ["quant_only"] = new(), ["spy_hold"] = new(),
            ["kospi200_hold"] = new(), ["monthly_80_20"] = new()
        };
        private StreamWriter _writer;

        public override void Initialize()
        {
            SetTimeZone(TimeZones.Utc);
            SetStartDate(2020, 1, 1);
            SetEndDate(DateTime.ParseExact(
                Environment.GetEnvironmentVariable("TA_RESEARCH_LEAN_END"), "yyyy-MM-dd", CultureInfo.InvariantCulture));
            SetCash(Initial);
            AddData<ResearchFrame>("RESEARCH", Resolution.Minute, TimeZones.Utc, fillForward: false);
            SetBenchmark(_ => Initial);
            _writer = new StreamWriter(Environment.GetEnvironmentVariable("TA_RESEARCH_LEAN_RESULT"));
        }

        public override void OnData(Slice slice)
        {
            foreach (var frame in slice.Get<ResearchFrame>().Values)
            {
                using var parsed = JsonDocument.Parse(frame.Payload);
                var data = parsed.RootElement;
                var market = data.GetProperty("market").GetString();
                var day = data.GetProperty("day").GetString();
                var open = data.GetProperty("open").GetBoolean();
                var fx = data.GetProperty("fx").GetDecimal();
                foreach (var (name, account) in _accounts)
                {
                    var block = data.GetProperty("arms").GetProperty(name);
                    var prices = account.Observe(block.GetProperty("bars"), market, open);
                    var targets = block.GetProperty("targets");
                    if (open && targets.ValueKind == JsonValueKind.Object)
                    {
                        account.Rebalance(prices, targets, market, int.Parse(day.Substring(0, 4)), fx);
                    }
                    if (data.GetProperty("mark").GetBoolean())
                    {
                        _writer.WriteLine(JsonSerializer.Serialize(new
                        {
                            day, arm = name, nav = account.NetValue(fx), fills = account.FillCount
                        }));
                    }
                }
            }
        }

        public override void OnEndOfAlgorithm() => _writer?.Dispose();

        private sealed class Position
        {
            public int Shares;
            public decimal Basis;
            public decimal Price;
            public bool IsUsd;
        }

        private sealed class Account
        {
            private readonly SortedDictionary<string, Position> _positions = new(StringComparer.Ordinal);
            private readonly Dictionary<int, decimal> _gains = new();
            private decimal _cash = Initial;
            private decimal _dividendUsd;
            private decimal _dividendKrw;
            public int FillCount { get; private set; }
            private decimal Reserve => _gains.Values.Sum(gain => Math.Max(0m, gain - 2_500_000m) * .22m);

            public decimal NetValue(decimal fx) => _cash + _dividendKrw + fx * _dividendUsd - Reserve +
                _positions.Values.Sum(p => p.Shares * p.Price * (p.IsUsd ? fx : 1m));

            public Dictionary<string, decimal> Observe(JsonElement bars, string market, bool open)
            {
                var prices = new Dictionary<string, decimal>();
                foreach (var entry in bars.EnumerateObject())
                {
                    var usd = market == "US";
                    if (!_positions.TryGetValue(entry.Name, out var position))
                    {
                        position = new Position { IsUsd = usd };
                        _positions.Add(entry.Name, position);
                    }
                    var bar = entry.Value;
                    if (open && position.Shares > 0)
                    {
                        var split = bar.GetProperty("split").GetDecimal();
                        var shares = position.Shares * split;
                        if (shares != decimal.Truncate(shares))
                        {
                            throw new InvalidOperationException("Missing fractional split settlement.");
                        }
                        position.Shares = (int)shares;
                        var income = position.Shares * bar.GetProperty("dividend").GetDecimal();
                        if (usd) _dividendUsd += income * .85m;
                        else _dividendKrw += income * .846m;
                    }
                    position.Price = prices[entry.Name] = bar.GetProperty(open ? "open" : "close").GetDecimal();
                }
                return prices;
            }

            public void Rebalance(Dictionary<string, decimal> prices, JsonElement targets, string market, int year, decimal fx)
            {
                var usd = market == "US";
                var rate = usd ? fx : 1m;
                var spread = usd ? .001m : 0m;
                var nav = Math.Max(0, NetValue(fx));
                var orders = prices.Select(mark =>
                {
                    var weight = targets.TryGetProperty(mark.Key, out var value) ? value.GetDecimal() : 0m;
                    return (Symbol: mark.Key,
                            Qty: (int)decimal.Floor(nav * weight / (mark.Value * rate)) - _positions[mark.Key].Shares);
                }).OrderBy(order => order.Qty >= 0).ThenBy(order => order.Symbol, StringComparer.Ordinal).ToArray();

                foreach (var (symbol, desired) in orders)
                {
                    var quote = prices[symbol];
                    var qty = desired;
                    var position = _positions[symbol];
                    if (qty > 0)
                    {
                        qty = Math.Min(qty, (int)decimal.Floor(Math.Max(0m, _cash - Reserve) /
                            (quote * rate * 1.001m * 1.001m * (1m + spread))));
                        if (qty == 0) continue;
                        var cost = qty * quote * 1.001m * 1.001m * rate * (1m + spread);
                        position.Basis += cost;
                        _cash -= cost;
                    }
                    else if (qty < 0)
                    {
                        decimal levy = usd || symbol == "069500.KS" ? 0m : year switch
                        {
                            2020 => .0025m, 2021 or 2022 => .0023m,
                            2023 or 2026 => .002m, 2024 => .0018m, 2025 => .0015m,
                            _ => throw new InvalidOperationException("Missing KOSPI tax scenario.")
                        };
                        var proceeds = (-qty) * quote * .999m * (.999m - levy) * rate * (1m - spread);
                        var soldBasis = position.Basis * (-qty) / position.Shares;
                        position.Basis -= soldBasis;
                        if (usd) _gains[year] = _gains.GetValueOrDefault(year) + proceeds - soldBasis;
                        _cash += proceeds;
                    }
                    else continue;
                    position.Shares += qty;
                    FillCount++;
                }
            }
        }
    }

    public sealed class ResearchFrame : BaseData
    {
        public string Payload { get; init; }
        public override SubscriptionDataSource GetSource(SubscriptionDataConfig config, DateTime date, bool live) =>
            new (Path.Combine(Environment.GetEnvironmentVariable("TA_RESEARCH_LEAN_TAPE"),
                              date.ToString("yyyyMM", CultureInfo.InvariantCulture) + ".csv"),
                 SubscriptionTransportMedium.LocalFile);

        public override BaseData Reader(SubscriptionDataConfig config, string line, DateTime date, bool live)
        {
            if (string.IsNullOrWhiteSpace(line)) return null;
            var comma = line.IndexOf(',');
            var time = DateTime.ParseExact(line.Substring(0, comma), "yyyyMMdd HHmmss", CultureInfo.InvariantCulture);
            return time.Date == date.Date
                ? new ResearchFrame { Symbol = config.Symbol, Time = time, Value = 1, Payload = line[(comma + 1)..] }
                : null;
        }
    }
}
