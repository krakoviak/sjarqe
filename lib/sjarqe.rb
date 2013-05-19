VOWEL = {:nil => 5, :a => 6, :ya => 3, :e => 5, :ye => 2, :u => 6, :i => 3, :o => 7, :yo => 2, :aa => 0, :ee => 0, :uu => 0, :ii => 0, :oo => 0, :ai => 3, :ei => 3, :yei => 1, :oi => 2, :ou => 2, :au => 2}
CONSONANT = {:nil => 5, :y => 4, :q => 4, :kh => 4, :w => 3, :r => 7, :R => 5, :t => 7, :p => 6, :s => 8, :d => 8, :f => 3, :g => 4, :x => 4, :k => 6, :l => 6, :z => 7, :v => 6, :b => 3, :n => 5, :m => 5, :sj => 4, :dj => 4, :ch => 4, :th => 6, :dh => 6, :j => 2, :ts => 5, :dz => 5}

TEXT = {:verse => %w(a4 a4 a4 a4), :structure => [:verse, :line, :verse]}
#TEXT = {:verse => %w(a4 b4 a4 b4), :structure => [:verse]}
#TEXT = {:verse => %w(a4 b4 a4 b4), :chorus => %w(a6 a6 b6 b6 c4 c4), :structure => [:verse, :line, :chorus]}

MAX_CONSONANT_SEQUENCE = 2
MAX_VOWEL_COUNT = 2
MIN_VOWEL_COUNT = 1
CLOSED_SYLLABLE_FREQUENCY = 4
LONGER_WORDS_FREQUENCY = 7

def generate structure
  assimilations = load 'assimilation_rules'
  palatalizations = load 'palatalizations'
  palatalizers = load 'palatalizers'
  cons_rhyme = load 'consonant_rhyme'

  structure[:structure].each do |text_block|
    if text_block == :line
      puts
    else
      # map line type to the last two rhyme-forming vowels in the line
      rhymes = {}
      structure[text_block].each do |line_type|
        rhyme_key = line_type.scan(/[a-z]/).join.to_sym
        rhymes[rhyme_key] ||= { :c2 => get(CONSONANT), :v2 => get(VOWEL), :c1 => get(CONSONANT), :v1 => get(VOWEL) }
        #puts rhymes[rhyme_key]

        vowel_count = line_type.scan(/\d+/).join.to_i
        rhyme = rhymes[rhyme_key]

        line = []

        #vowel counter
        i = 0

        # to avoid consonant clusters at word start
        word_start = true

        cons_sequence = 0
        vowels_in_last_word = 0

        while i < vowel_count

          if (word_start && cons_sequence == 0) || (!word_start && cons_sequence < MAX_CONSONANT_SEQUENCE)
            consonant = (vowel_count - i) <= 2 ? cons_rhyme[rhyme["c#{(vowel_count - i)}".to_sym].to_s].split.sample : get(CONSONANT)
            line << consonant.to_s
            cons_sequence += 1
            word_start = false
          end

          vowel = vowel_count - i <= 2 ? rhyme["v#{vowel_count - i}".to_sym] : get(VOWEL)

          i += 1
          vowels_in_last_word += 1

          line << vowel.to_s

          cons_sequence = 0
          word_start = false

          # inserting a whitespace
          # tune word length: the first part (before ||) is for max syllable count,
          # the second part is for probability of inserting a whitespace (the greater the value the shorter the words)
          # also here we make sure no words with no vowels appear
          if (vowels_in_last_word >= MAX_VOWEL_COUNT || (rand(10) > LONGER_WORDS_FREQUENCY && vowels_in_last_word >= MIN_VOWEL_COUNT)) && i < vowel_count
            line << ' '
            vowels_in_last_word = 0
            cons_sequence = 0
            word_start = true
          end

          # closed syllables are still needed, but not many
          if rand(10) > CLOSED_SYLLABLE_FREQUENCY && ((word_start && cons_sequence == 0) || (!word_start && cons_sequence < MAX_CONSONANT_SEQUENCE))
            line << get(CONSONANT).to_s
            cons_sequence += 1
          end
        end

        #puts line.join

        # apply assimilations & palatalizations
        (0...line.size).each do |i|
          if line[i + 1] && line[i + 1].strip != ''
            key = "#{line[i]}|#{line[i + 1]}"
            while assimilations[key]
              rule = assimilations[key].split('|')
              line[i] = rule[0]
              line[i + 1] = rule[1]
              key = "#{line[i]}|#{line[i + 1]}"
            end

            if palatalizations[line[i]] && palatalizers[line[i + 1]]
              line[i] = palatalizations[line[i]]
              line[i + 1] = palatalizers[line[i + 1]]
            end
          end
        end

        puts line.join
      end
    end
  end
end

def get letters
  until letters[random_letter = letters.keys.sample] > rand(10) && random_letter != :nil
    random_letter = letters.keys.sample
  end
  random_letter
end

def load file
  hash = {}
  IO.foreach("./#{file}") do |line|
    if line.strip[0] != '#' && line.include?('=>')
      rule = line.split('=>')
      hash[rule[0].strip] = rule[1].strip
    end
  end
  hash
end

generate TEXT