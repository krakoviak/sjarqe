VOWELS = {:nil => 5, :a => 6, :ya => 3, :e => 5, :ye => 2, :u => 6, :i => 3, :o => 7, :yo => 2, :aa => 0, :ee => 0, :uu => 0, :ii => 0, :oo => 0, :ai => 3, :ei => 3, :yei => 1, :oi => 2, :ou => 2, :au => 2}
CONSONANTS = {:nil => 5, :y => 4, :q => 4, :kh => 4, :w => 3, :r => 7, :R => 5, :t => 7, :p => 6, :s => 8, :d => 8, :f => 3, :g => 4, :x => 4, :k => 6, :l => 6, :z => 7, :v => 6, :b => 3, :n => 5, :m => 5, :sj => 4, :dj => 4, :ch => 4, :th => 6, :dh => 6, :j => 2, :ts => 5, :dz => 5}

STRUCTURE = {:verse => %w(a7 a5 a7 a5), :structure => [:verse, :line, :verse]}
#STRUCTURE = {:verse => %w(a4 b4 a4 b4), :structure => [:verse]}
#STRUCTURE = {:verse => %w(a4 b4 a4 b4), :chorus => %w(a6 a6 b6 b6 c4 c4), :structure => [:verse, :line, :chorus]}

MAX_CONSONANT_SEQUENCE = 2
MAX_VOWEL_COUNT = 2
MIN_VOWEL_COUNT = 1
CLOSED_SYLLABLE_FREQUENCY = 4
LONGER_WORDS_FREQUENCY = 7

def generate_text_from_structure structure
  $assimilations = load_rules 'assimilation_rules'
  $palatalizations = load_rules 'palatalizations'
  $palatalizers = load_rules 'palatalizers'
  $cons_rhyme = load_rules 'consonant_rhyme'

  structure[:structure].each do |i|
    i == :line ? puts : print_lines(structure[i])
  end
end

# %w(a10 b8 a10 b8)
def print_lines struct
  # map line type to the last two rhyme-forming vowels in the line
  rhymes = {}
  struct.each do |i|
    rhyme_key = i.scan(/[a-z]/).join.to_sym
    rhymes[rhyme_key] ||= { :c2 => get_letter(CONSONANTS), :v2 => get_letter(VOWELS), :c1 => get_letter(CONSONANTS), :v1 => get_letter(VOWELS) }
    #puts rhymes[rhyme_key]
    line = generate_line i.scan(/\d+/).join.to_i, rhymes[rhyme_key]
    puts line
  end

end

# returns last letter added to the current word; if none found returns ''
def get_last_added_letter line
  line[-1].nil? || line[-1]  == ' ' || line[-1].strip.size == 0 ? '' : line[-1].strip
end

def generate_line vowel_count, rhyme
  line = []

  #vowel counter
  i = 0

  # to avoid consonant clusters at word start
  word_start = true

  cons_sequence = 0
  vowels_in_last_word = 0

  while i < vowel_count

    if (word_start && cons_sequence == 0) || (!word_start && cons_sequence < MAX_CONSONANT_SEQUENCE)
      consonant = (vowel_count - i) <= 2 ? $cons_rhyme[rhyme["c#{(vowel_count - i)}".to_sym].to_s].split.sample : get_letter(CONSONANTS)
      line << consonant.to_s
      cons_sequence += 1
      word_start = false
    end

    vowel = vowel_count - i <= 2 ? rhyme["v#{vowel_count - i}".to_sym] : get_letter(VOWELS)

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
      line << get_letter(CONSONANTS).to_s
      cons_sequence += 1
    end
  end

  apply_assimilations(line).join
end

def get_letter letters
  until letters[random_letter = letters.keys.sample] > rand(10) && random_letter != :nil
    random_letter = letters.keys.sample
  end
  random_letter
end

def apply_assimilations line

  (0...line.size).each do |i|
    if line[i + 1] && line[i + 1].strip != ''
      key = "#{line[i]}|#{line[i + 1]}"
      while $assimilations[key]
        rule = $assimilations[key].split('|')
        line[i] = rule[0]
        line[i + 1] = rule[1]
        key = "#{line[i]}|#{line[i + 1]}"
      end

      if $palatalizations[line[i]] && $palatalizers[line[i + 1]]
        line[i] = $palatalizations[line[i]]
        line[i + 1] = $palatalizers[line[i + 1]]
      end
    end
  end

  line
end

def load_rules file
  hash = {}
  IO.foreach("./#{file}") do |line|
    if line.strip[0] != '#' && line.include?('=>')
      rule = line.split('=>')
      hash[rule[0].strip] = rule[1].strip
    end
  end
  hash
end

generate_text_from_structure STRUCTURE

#20.times { puts get_letter CONSONANTS }

#puts load_rules 'assimilation_rules'
